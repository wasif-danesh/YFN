# Greater Melbourne real-data sample

Prepared 8 September 2026 for **Your Friendly Neighbourhood** database and ER-diagram design. Includes all **361 spatial SA2s in ASGS 2021 GCCSA `2GMEL`**, with four indicator records each: **1,444 observations** and **2,166 annual population records**. Inputs are real official data. Spatial definitions remain provisional; this is not an approved public or assessment release.

## Start here

- [Summary CSV](sample-summary.csv): one row per SA2, including values, population denominators, transport coverage and quality notes.
- [SQLite database](yfn.sqlite): normalized tables, constraints, indexes and a summary view, populated from the curated CSVs.
- [ER diagram and schema guide](schema-guide.md); [editable Mermaid source](schema-erd.mmd).
- [Executable SQL schema](../../pipeline/greater_melbourne_schema.sql).
- [Full column dictionary](data-dictionary.md).
- [Validation report](audit/validation-report.json), [test results](audit/test-results.txt) and [offline rebuild comparison](audit/rebuild-check.json).

The original four-area package has been retired. A compact [regression fixture](../../pipeline/fixtures/four-area-regression.json) preserves its independently checked values; no second database is required.

## Availability

| Indicator | Numeric result | Unavailable | Meaning |
|---|---:|---:|---|
| Census median weekly rent | 358 | 3 | AUD/week reported in **2021**, not current advertised rent |
| Population change | 359 | 2 | Percentage change in ERP, 30 June 2020 to 30 June 2025 |
| Transport | 360 | 1 | Area-weighted raw morning access index over covered land; all numeric results marked limited |
| Selected public open space | 354 | 7 | Unioned selected inventory area / 2025 ERP; all numeric results marked limited |

Every SA2 still has all four observation rows. A missing measure has a null raw value and an explicit reason. No synthetic values, fabricated estimates, transport percentiles or rating labels are inserted.

### Geography and population

Selection uses `GCC_CODE21 = '2GMEL'` from the original ABS boundary file, not a list of suburb names or council boundaries. The geography includes outer areas such as Macedon, Romsey and Bacchus Marsh. SA2s are not exact suburb boundaries. The database retains the 2021 edition even though acquisition occurred in 2026.

West Melbourne - Industrial and Royal Botanic Gardens Victoria have zero ERP throughout 2020–2025. They remain in `areas` and `population_history`, but `is_comparable = 0` and growth/per-resident values are unavailable. The other 359 areas have positive 2025 ERP and `is_comparable = 1` under the sample rule. This flag does not approve a production scoring cohort or a small-population eligibility threshold.

The six annual SA2 population totals exactly match the independently published Greater Melbourne totals in the workbook's Table 4. The 2025 total is **5,435,590 residents**. 2020–2021 values are final, 2022–2024 revised and 2025 preliminary. Growth uses estimates from one release on compatible geography; it is not a forecast.

### Rent zeros

The source G02 file contains `0` for West Melbourne - Industrial, Royal Botanic Gardens Victoria and Essendon Airport. All three official QuickStats pages say the area had no people or a very low Census population. The 2021 RNTD definition excludes zero rent. These entries are therefore preserved as original tokens in the source audit and represented as unavailable medians in observations, never as free rent. The source does not distinguish a precise suppression reason here, so none is invented.

### Transport coverage

Of the 360 numeric transport results, 354 are **available** and 6 are **limited** because the data covers less than half of the area. They are land-area-weighted averages, not scores out of 100 or measures of access from a rental address. Macedon has no PTAL intersection and a null result. Outer areas can have very small covered fractions: for example, Romsey is approximately 0.32%, Gisborne 0.94% and Kinglake 1.91%. Do not interpret these covered-land averages as representative of their entire SA2s.

`coverage_fraction` is valid PTAL union area divided by SA2 area. Unknown land outside the source coverage is not assigned zero access. No minimum eligibility threshold or percentile has been silently selected. The full-area list is available for choosing a fixed benchmark later, but it is not itself an approved benchmark.

The numeric source is `sum_ai_8_9`; categorical `category_8_9` is retained in the intersection audit but never averaged. The linked December 2025 fact sheet describes services from 2 April 2025, 08:00–09:00. Its exact correspondence to the downloaded live layer is unverified, so the observation date stays null. Download dates do not become service dates.

### Open-space definition and gaps

The sample retains the earlier explicit filter:

- `OS_TYPE = Public open space`
- `OS_ACCESS = Open`
- `OS_STATUS = Existing`
- `OS_CATEGOR` in Parks and gardens; Natural and semi-natural open space; Recreation corridor; Sportsfields and organised recreation.

Selected polygons are unioned before their area is counted, avoiding overlapping parcels being counted twice. Categories such as Conservation reserves are excluded by this filter; this is a deliberate choice, not a claim that they are unusable public space. Water bodies recorded as open space are included. Source attributes and exclusion reasons remain in the audit.

Five SA2s have no selected inventory polygons: Moorabbin Airport, Essendon Airport, Gisborne, Macedon and Riddells Creek. With unknown inventory coverage, this cannot establish zero real open space. Their per-resident observations are null. Two additional areas have zero population. The diagnostic inventory area can be zero even while the displayed indicator is unavailable.

The source is unmaintained and its observation date/completeness is unverified. It contains sports facilities and water/river polygons, so the indicator is labelled **selected public open space**, not confirmed vegetation, current park access or walking distance. The optional diagnostic excluding records explicitly marked `WATER_BODY = Yes` is retained; blank flags remain unknown. For example, Footscray changes from 38.75 to 32.61 m²/person under that alternative. It is a sensitivity check, not a second approved indicator.

Low population can produce very large ratios: Braeside has approximately 118,881 m² of selected inventory space per resident. This is not a calculation cap or a recommended renter ranking. Review the actual population denominator and area function before deciding production eligibility; no arbitrary low-population threshold has been imposed.

## Sources and traceability

| Publisher and release | Use | Verification |
|---|---|---|
| [ABS Census 2021 DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | Victoria SA2 G02 `Median_rent_weekly` | Exact codes; all source rows preserved; 14 separate QuickStats pages checked, including 11 numeric matches and 3 unavailability notices |
| [ABS Regional population 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | Table 1 ERP, 2020–2025 | Exact codes/names/GCCSA; six annual sums reconcile to Table 4 |
| [ABS ASGS Edition 3 boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files) | SA2 identity, Greater Melbourne membership and geometry | Original GDA2020 shapefile re-extracted offline |
| [DataVic PTAL](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro) | Raw morning transport index | Entire layer: 360,662 unique cells; source count stable before/after acquisition |
| [DataVic Open Space](https://discover.data.vic.gov.au/dataset/open-space) | Public open-space inventory | Entire layer: 38,810 unique features; full object-ID inventory reconciled before/after acquisition |

The [acquisition manifest](acquisition.json) records 178 exact downloaded filenames, query URLs, timestamps, sizes and SHA-256 hashes. The three ABS bulk files and original metadata snapshots are reused byte-for-byte from the earlier sample. Spatial layers and QuickStats pages are separately acquired. Licences and source limitations are in `curated/data_sources.csv`; exact resource URLs are in `curated/source_files.csv`.

Processing area CRS is EPSG:7855 (GDA2020 / MGA zone 55). ABS/PTAL inputs are EPSG:7844; open-space inputs are EPSG:3857. The latter transformation reports 3 m positional accuracy, so metre-square numeric precision is computational precision, not a claim of survey accuracy.

## What was verified

- All 361 boundary identities join exactly to Census and ERP; every area has four observations and six annual records.
- All raw snapshot hashes, complete-layer counts and unique IDs reconcile. Pagination does not silently lose or duplicate features. These checks establish saved-source completeness, not current ground truth.
- Spatial calculations check valid geometry, intersection limits, PTAL overlap, independent Decimal weighted sums and projected/geodesic area agreement. Open-space union-before-clip agrees with clip-before-union.
- Nine open-space geometries required repair; their area changes are below 0.01 m². The raw geometry is retained unchanged.
- 41,177 intersecting source-feature/SA2 records were compared with publisher-stored hectares. Twelve comparisons across eight distinct features differ by more than the original 0.51 m² rounding allowance; the largest difference is 8.23 m². All exceptions are below 0.01% relative difference and are retained in `audit/source-hectare-exceptions.json`. Calculations use geometry, not the rounded source area attribute.
- SQLite integrity, foreign keys, null handling, negative growth, source relationships and read-only runtime access are checked. All **17 tests pass**, including the original spatial edge cases and a check that the ER diagram matches every table, foreign-key relationship and selected column.
- **30 data and documentation files reproduced byte-for-byte** in an offline rebuild in the same runtime. The rebuild report records their hashes and the measured rebuild duration.

Source checks and calculations are verified to this documented scope. Production scoring, acceptable spatial coverage, the open-space filter and current ground access remain unresolved. No external deployment or application implementation is part of this package.

## Rebuild and development use

From the project root, use Python 3.12 with `pipeline/requirements-greater-melbourne.txt` installed in a virtual environment. This pins the sample's spatial/workbook libraries and NumPy. Do not use Python `-O`: assertions intentionally stop invalid builds.

```sh
python pipeline/acquire_greater_melbourne.py
python pipeline/build_greater_melbourne.py
python pipeline/document_greater_melbourne.py
python -m unittest discover -s pipeline -p 'test_*.py' -v
python pipeline/verify_greater_melbourne_rebuild.py
```

Only acquisition uses the network. Cached raw inputs are checksummed; rerunning acquisition refreshes the end-of-download inventory checks and therefore changes the acquisition manifest. For a byte-identical rebuild, rerun the builder against the same saved acquisition, without reacquiring. Acquisition and rebuilding are self-contained: source URLs and paths are in `pipeline/melbourne_config.py`, with shared calculations in `pipeline/melbourne_common.py`. No earlier sample folder is required.

`curated/*.csv` is the normalized interchange format. Blank numeric cells mean null; identifiers must be imported as text. Read `yfn.sqlite` in read-only mode from a REST service; the UI can consume the same observation shape with synthetic or real content. This package supplies data and a tested schema example, not a finalized API contract. Geometry and raw downloads need not be shipped with the API.
