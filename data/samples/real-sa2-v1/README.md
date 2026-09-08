# Real SA2 sample for database design

Created 8 September 2026 from official source downloads and public spatial services. This sample contains four SA2s, all four indicator categories, 16 observations and 24 annual population records. The records are real. The transport aggregation and open-space filter are explicitly provisional sample methods, and this is not an approved public release.

**Start with [sample-summary.csv](sample-summary.csv) or [sample-summary.json](sample-summary.json).** The populated [sample.sqlite](sample.sqlite) database and [curated CSVs](curated/) contain the same results with provenance and calculation components. [The SQL schema](../../../pipeline/sample_schema.sql) is an executable design example, not a final schema decision.

| Official 2021 SA2 | SA2 code | 2021 Census rent, AUD/week | Estimated growth 2020–2025 | Raw transport index, sample mean | Selected public open space, sample m²/person |
|---|---|---:|---:|---:|---:|
| Carlton | 206041117 | 365 | 21.10% | 41.82 | 11.09 |
| Clayton (North) - Notting Hill | 212051567 | 380 | 27.28% | 7.48 | 3.61 |
| Clayton - Central | 212051568 | 401 | 10.38% | 8.77 | 5.05 |
| Footscray | 213031348 | 355 | 15.42% | 24.85 | 38.75 |

The transport column is **not a score out of 100**. Open space includes selected public sports grounds and natural open space, including some river/water polygons. It is not measured vegetation cover, park walking access or current ground truth. All calculations retain full precision in CSV, JSON and SQLite; the table is rounded for reading.

**How the values were verified**

- Area codes and names were extracted from the original ABS 2021 SA2 shapefile. All four belong to Greater Melbourne (`2GMEL`). They join exactly to the Census and ERP records. There is no exact SA2 called simply “Clayton” in this boundary edition.
- Rent was read from G02 `Median_rent_weekly`, whose supplied dictionary identifies cell G112. All four values match the separate official [Carlton](https://www.abs.gov.au/census/find-census-data/quickstats/2021/206041117), [Footscray](https://www.abs.gov.au/census/find-census-data/quickstats/2021/213031348), [Clayton - Central](https://www.abs.gov.au/census/find-census-data/quickstats/2021/212051568) and [Clayton (North) - Notting Hill](https://www.abs.gov.au/census/find-census-data/quickstats/2021/212051567) QuickStats pages. These pages are verification references, not scraped pipeline inputs.
- The ERP workbook's Table 1 supplies six annual values, 2020 through 2025. Exact worksheet cell locators are retained in `population_history.csv`. The percentage is calculated from 2020 and 2025 values in the same release. New 2021 Clayton codes have historical estimates in this workbook, so no cross-edition name matching was necessary.
- Spatial candidate counts match each service response, and IDs are unique within each query. Bounding boxes acquire candidates; exact polygons determine the final intersection. Geometry calculations use GDA2020 / MGA zone 55 (EPSG:7855), not degrees or Web Mercator area.
- Valid transport polygons cover effectively 100% of each sampled SA2, to floating-point tolerance. There are no material overlapping PTAL cells. This says nothing about coverage elsewhere in Melbourne.
- Open-space polygons were dissolved to avoid counting overlaps twice. Footscray had approximately 516.38 m² of overlapping selected geometry removed. Dissolving before clipping and clipping before dissolving produce equivalent results within 0.01 m².
- The calculated full-feature park areas agree with 293 source hectare entries within 0.50 m², consistent with the stored hectare rounding. A separate geodesic calculation corroborates projected areas within the stated 0.2% sanity tolerance. These tolerances test arithmetic and topology; they are not data-coverage eligibility thresholds.
- One distinct open-space feature, FID 9800, needed geometry repair. It occurred in two area query sets and both repairs are logged; the area change was negligible.
- SQLite integrity and foreign-key checks pass. Six regression tests cover missing/zero values, population decline, Esri polygon holes, overlapping/cross-boundary parcels, database constraints and read-only connections. Persisted components independently reconstruct the derived results.
- An offline second build produced byte-identical versions of all 13 checked outputs, including the SQLite database, in the same environment.

See [validation report](audit/validation-report.json), [spatial diagnostics](audit/spatial-validation.json), [rebuild evidence](audit/rebuild-check.json) and [test results](audit/test-results.txt). This verifies extraction and computation under stated methods. It does not establish present-day inventory completeness, visit every park, approve the methodology or validate full-Melbourne ratings.

**Source meanings and sample decisions**

Rent is the 2021 Census median reported weekly rent for occupied private dwellings being rented. The supplied G02 footnotes exclude rent-free dwellings, visitor-only households and other non-classifiable households. It is not current advertised rent or a particular property's rent. The source notes that its treatment of rent-free dwellings differs from 2016.

Population is ABS Estimated Resident Population at 30 June, not the Census-night population count. For this release 2020–2021 are final, 2022–2024 revised and 2025 preliminary. The formula is `100 × (population_2025 − population_2020) / population_2020`. The source release and each year's revision status are retained. [ABS release and workbook](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25), [methodology](https://www.abs.gov.au/methodologies/regional-population-methodology/2024-25).

Transport uses the actual numeric field `sum_ai_8_9`, not numeric encodings of `category_8_9`. The sample formula is `sum(cell intersection area × access index) / sum(valid cell intersection area)`. Every intersecting source cell and weighted term is retained in `audit/ptal-intersections.csv`. The linked [December 2025 fact sheet](https://www.planning.vic.gov.au/__data/assets/pdf_file/0033/762738/PTAL-Fact-Sheet-December-2025.pdf) describes 8–9 am services on 2 April 2025. The live layer lacks per-feature dates; the sample leaves its exact observation date null rather than asserting that the current layer uses that snapshot. Its catalogue update date is a separate piece of metadata. Direct PDF download returned HTTP 403, but the document was readable through the research tool; it is linked rather than presented as an archived download.

No transport percentile, rating, benchmark cohort or minimum coverage threshold is assigned. Those require agreed production decisions and a full eligible Melbourne cohort. A four-area comparison cannot establish that cohort.

For open space the **sample-only** eligibility rule is all of:

1. `OS_TYPE = Public open space`;
2. `OS_ACCESS = Open`;
3. `OS_STATUS = Existing`;
4. `OS_CATEGOR` is Parks and gardens, Natural and semi-natural open space, Recreation corridor, or Sportsfields and organised recreation.

The union of these polygons within each SA2 is divided by 2025 ERP. Fields and labels were inspected before selecting this rule. Every intersecting parcel retains its inclusion/exclusion decision, name, category, access, land type, water flag and clipped area in `audit/open-space-intersections.csv`. Ownership alone does not determine eligibility. Source `HA` is only a check; clipping is calculated from geometry.

The [open-space catalogue](https://discover.data.vic.gov.au/dataset/open-space) says the inventory is not maintained. Its actual observation date and current completeness remain unknown. `coverage_fraction` is therefore null for this indicator; the percentage of land occupied by parks is not an inventory-completeness measure. The original layer uses EPSG:3857; the recorded datum transformation to GDA2020 has stated 3 m accuracy, which limits boundary precision.

The water flag matters: excluding selected parcels explicitly marked `WATER_BODY = Yes` changes Footscray from **38.75 to 32.61 m²/person**. The other three samples are unchanged. Blank flags remain unknown, so that alternative still cannot be called verified green cover. The broader filter including all existing, open, public-open-space categories is also retained as a sensitivity calculation in the spatial diagnostics. Neither alternative is an approved production rule.

**Implications for the database schema**

| Real-data finding | Schema requirement demonstrated here |
|---|---|
| A suburb-like name can refer to distinct official areas | String SA2 code and boundary edition identify an area. Add verified aliases separately when needed; never use display names as join keys. |
| An official index and a project percentile have different units | Store `raw_value` and indicator unit separately from nullable `score` and `rating`. |
| Real inputs can support an unapproved derived method | Store `data_mode`, data quality, method approval status and publication readiness separately. |
| Sources have different dates, sometimes unknown | Allow nullable observation dates; retain reference-period text, download time and source release separately. |
| Population estimates can be revised | Store annual history with source release and revision status. |
| Open-space ratios combine geometry and population | Use many-to-many observation/source links and store numerator/denominator components with units and dates. |
| One source has several downloaded query files | Separate source dataset identity from source-file URLs, hashes and retrieval timestamps. |
| A changed category or water filter changes results | Store a versioned method definition and preserve feature classifications in pipeline audit data. |

The sample SQLite database implements these relationships. It has one boundary edition and one current observation per area/indicator in this release; multi-edition or multiple historical indicator releases would require extended keys. It is not a complete production schema. Detailed geometries and parcel audits can remain pipeline artifacts rather than API tables.

**Files and rebuilding**

`curated/` contains nine CSVs: areas, indicators, methods, observations, population history, data sources, source files, observation-source links and observation components. UTF-8 CSVs use an empty field for SQL null, decimal numbers without formatting, and plain string identifiers. Do not save identifiers through spreadsheet software that changes their type. JSON uses genuine nulls. The SQLite loader reads these CSVs directly, exercises constraints and writes a replacement file before swapping it into place.

`acquisition.json` records 20 downloaded files, exact URLs, retrieval timestamps, sizes and SHA-256 hashes. `raw/` retains the original ABS archives/workbook and service responses locally and is excluded from Git. `selected-sa2.geojson` is a derived inspection artifact; the builder re-extracts geometry from the original ABS archive. `audit/` holds field mappings, source rows, spatial calculations and test evidence.

From the project root, using Python 3.12 and the dependencies in `pipeline/requirements-sample.txt`:

```bash
python pipeline/acquire_real_sample.py
python pipeline/build_real_sample.py
python pipeline/test_real_sample.py
```

The acquisition command requires network access and curl. The other commands run offline. The original snapshots are cached; a changed checksum stops the build. Live services can change, so reacquiring a missing historical response may not reproduce this release. Preserve these raw snapshots for exact reconstruction. Do not run the builder with `python -O`, which disables its validation assertions. Runtime versions are recorded in `manifest.json`.

For an API, open `sample.sqlite` with SQLite URI `mode=ro`. For a quick inspection:

```sql
SELECT * FROM v_area_summary;
SELECT * FROM observations WHERE sa2_code = '212051568';
SELECT * FROM population_history WHERE sa2_code = '212051568' ORDER BY year;
```

No REST service, UI, GitHub push or external deployment was created in this sample task.

**Attribution**

Source: Australian Bureau of Statistics, 2021 Census GCP G02 and ASGS Edition 3 boundaries; Regional population 2024–25 released 31 March 2026. Population growth and ratios are based on ABS data and were calculated for this sample. ABS data used with permission from the Australian Bureau of Statistics. [ABS](https://www.abs.gov.au/), [copyright and attribution terms](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer).

Transport source: Victorian Department of Transport and Planning, [PTAL Melbourne metro](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro). Open-space source: Victorian Planning Authority, [Open Space](https://discover.data.vic.gov.au/dataset/open-space). These sources identify CC BY 4.0 licensing. All inputs were accessed 8 September 2026. The derived SA2 transport and open-space values are project sample calculations, not official published SA2 statistics or endorsements.
