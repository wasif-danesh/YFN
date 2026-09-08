# Data preparation, schema and API contract

Status: recommended implementation draft, 8 September 2026. This is not a claim that data has been downloaded, inspected or approved. Agree this contract at the start so all team members can work independently.

Subsequent evidence, 8 September 2026: a [four-SA2 real-data sample](../data/samples/real-sa2-v1/README.md) now contains source-checked Census rent, 2020–2025 ERP and reproducible sample spatial calculations. Its CSVs, SQLite schema, field mappings and validation reports inform this proposal; they do not approve the provisional transport weighting, open-space filter or production scoring. The original draft below remains a proposal for team review.

The user subsequently requested the [complete Greater Melbourne sample](../data/samples/greater-melbourne-v1/README.md). It now covers all 361 spatial SA2s with four observation rows each, including unavailable values. Use its [ER diagram and schema guide](../data/samples/greater-melbourne-v1/schema-guide.md) and [column dictionary](../data/samples/greater-melbourne-v1/data-dictionary.md) for concrete design evidence. The implemented sample adds comparison-eligibility notes, separate source files, method records, observation components and spatial diagnostics to the earlier proposal. It retains zero-population geographies, withholds ambiguous zero rent medians, and preserves partial PTAL coverage. The final shared application contract and production eligibility/scoring rules remain to be agreed.

## 1. Dataset register: both iterations

Inspect all five core sources at the start, including sources involving spatial work. Download links below are discovery pages taken from the project references; recheck their resources and licences before acquiring files. Exact filenames in the earlier specification are candidates and have not been verified in this handover.

| Source | Expected use and required semantic fields | Iteration |
|---|---|---|
| [ABS Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | 2021 Victoria SA2 General Community Profile, selected medians table (G02); area code and median weekly rent; dictionary and suppression/missing-value definitions | I1 core; I2 review newer sources separately |
| [ABS Regional Population](https://www.abs.gov.au/statistics/people/population/regional-population/latest-release) | Annual ERP, SA2 code, reference year, population, geography edition and revision details; check whether the proposed 2020-2025 interval is present on a consistent geography | I1 core; I2 refresh/version checks |
| [ABS 2021 SA2 geography](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/main-structure-and-greater-capital-city-statistical-areas/statistical-area-level-2) | Boundary resource: SA2 code/name, GCCSA code/name, geometry, CRS; use edition compatible with observations | I1 core; retain for I2 |
| [DataVic PTAL Melbourne metro](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro) | Geometry, numeric index or category, definitions, coverage and observation date; verify whether data is points, cells or polygons and which aggregation is justified | I1 target; I2 improve coverage/method |
| [DataVic Open Space](https://discover.data.vic.gov.au/dataset/open-space) | Geometry, feature identifier, category, ownership/access classification and observation date; older proposal flags it as unmaintained, which must be rechecked | I1 target; I2 evaluate maintained replacement |
| [Homes Victoria rental report](https://www.dffh.vic.gov.au/publications/rental-report) | Optional moving annual median rent by suburb, dwelling type, bedroom count, period, counts/suppression and geographic definition | I2 candidate, not a substitute silently joined to SA2 |
| [ABS suburbs/localities information](https://www.abs.gov.au/census/guide-census-data/geography/census-geography-glossary) | Optional SAL codes/names, boundary edition and defensible relationships to SA2 | I1/I2 timing to confirm |

Semantic names above are our requirements, not assertions about the actual file column names. Preserve original column names in a mapping dictionary once inspected. Keep GeoJSON/SHP sidecar files together when required. No web scraping is planned; use official open downloads or documented APIs.

## 2. Repeatable preparation

1. Register each file: publisher, original URL, resolved resource URL, filename, download date, reference period, boundary edition, licence, checksum and notes. Preserve raw files unchanged.
2. Profile sheets/layers and field types, unique area counts, duplicate keys, nulls, suppressed values, numeric ranges, CRS and invalid geometry. Check spatial coverage before committing to the method.
3. Produce source-specific staging tables. Keep identifiers as strings, numeric measures as numbers and missing values as null. Record rejected records with reasons.
4. Build the SA2 master from the chosen boundary edition. Filter Greater Melbourne by official GCCSA classification; exclude non-spatial special-purpose records. Retain a documented eligible set and distinguish missing indicators from ineligible areas.
5. Validate each source's join coverage against the master. Investigate unmatched codes instead of dropping them silently. Never assume different boundary editions are interchangeable.
6. For geometry: use a suitable projected CRS with metre units for area, record it, inspect repairs and dissolve eligible overlapping open-space polygons before intersection to prevent double counting.
7. Produce SA2 PTAL aggregates only after confirming how the underlying index should be aggregated; preserve the proportion of each area covered. Unknown outside-coverage land is not zero PTAL.
8. Apply a documented open-space eligibility filter, intersect with SA2s and calculate eligible square metres. Ownership alone may not prove public access. Exclude ambiguous categories from the eligible measure or flag uncertainty explicitly.
9. Join curated indicators and population history, calculate approved metrics and quality flags, and retain every source used in derived values.
10. Rebuild a new SQLite file with foreign keys enabled and parameterised bulk insertion in a transaction. Do not mutate the live database during requests.
11. Validate uniqueness, foreign keys, score bounds, source coverage, missing states and hand-calculated examples. Spot-check results against original sources before publication.
12. Publish a versioned database artefact and build manifest. Swap releases during deployment; preserve a previous validated release for rollback.

Suggested curated CSVs: `areas.csv`, `area_aliases.csv` (optional), `indicators.csv`, `observations.csv`, `population_history.csv`, `data_sources.csv` and `observation_sources.csv`. Intermediate transport/open-space tables can remain CSV/Parquet with geometry kept separately. Generated CSVs should not require hand edits.

## 3. Measure definitions

### Rent

Proposed I1: 2021 Census median weekly rent for the selected SA2, in AUD/week. Display source year beside the amount. No personal affordability or current-market claim. A ratio of area median rent to area median household income is not a household-level rent-burden statistic; the older pitch formula is not implemented by this baseline.

### Population change

For compatible ERP values P0 and P1 at years y0 and y1:

`growth_percent = 100 * (P1 - P0) / P0`

Proposed interval is 2020-2025, subject to actual source availability. If P0 is zero/missing, growth is unavailable. Negative growth is valid. A five-year interval needs endpoints five years apart; a complete annual series includes six observations. Never replace missing years with zero or extrapolate a forecast. Population estimates may be revised; preserve the release version.

### Transport: provisional method requiring source validation

If a defensible continuous numeric PTAL measure is supplied over non-overlapping polygons/cells, the v1.0 proposal is:

`raw_ptal = sum(valid_intersection_area * ptal_value) / sum(valid_intersection_area)`

Record `coverage_fraction = valid_covered_area / sa2_area`. Do not treat ordinal categories such as 1a/1b as equally spaced numbers without justification. If only categories are supplied, resolve a defensible alternative before computing scores. Points require a different sampling/coverage method; do not apply a polygon formula to them.

The minimum coverage threshold is unresolved. Do not invent one silently. Retain raw aggregates/coverage and withhold public scores until it is agreed. Area weighting can misrepresent access where residents occupy only part of a large SA2; label it as an area summary, not commute time or access from a property.

For valid comparable aggregates, a proposed deterministic percentile is:

`score = 100 * (average_rank - 1) / (n - 1)`

Ranks ascend, with average ranks for ties. Use all eligible, sufficiently covered Greater Melbourne SA2s with valid PTAL for that release, not just selected areas. Record this valid subset and n. With fewer than two valid values, score is null. If all values tie and n >= 2, each receives 50. Keep full precision for classification; round only the displayed number.

Proposed bands inherited from v1.0: score <25 Limited; 25 to <50 Moderate; 50 to <75 Stronger; 75 to 100 Very strong. These thresholds are project conventions, not official PTAL standards. Confirm wording and tie behaviour before releasing. A displayed rounded boundary value should not appear to contradict its label; the UI may need one decimal place near cutoffs.

### Green space

`sqm_per_resident = eligible_open_space_sqm_within_sa2 / population`

Use the same agreed population year across the release, and expose both open-space date and population year. If the population is non-positive/missing, result is null. A zero is valid only when coverage is sufficient and no eligible open space is present. Incomplete coverage yields unavailable/limited, not an apparent absence of parks. This measures provision inside the boundary, not walking access, quality or parks just outside it. Do not add a green-space score or land-area-share score without an agreed requirement.

### Shared rules

- No overall best-area score and no automatic good/bad classification of population growth or median rent.
- Every result includes units, periods, geographic coverage, sources, method version and quality.
- Use `available`, `limited` or `unavailable` for quality; include a reason when not available.
- Store a build-level `data_mode` of `synthetic` or `real`. Synthetic examples must be visibly identified during development and blocked from the final real-data release.

## 4. Recommended SQLite schema

This refines v1.0 to support multiple sources per derived value and one-to-many suburb mappings. It is a schema proposal, not an existing database.

| Table | Columns and constraints |
|---|---|
| `area` | `sa2_code TEXT PK`, `sa2_name`, `boundary_year`, `gccsa_code`, `gccsa_name`, `area_sq_km`, `is_eligible`. One boundary edition per release; future multi-edition storage needs a composite identity. |
| `area_alias` | `alias_id PK`, `alias_text`, `alias_normalized`, nullable `source_area_code`, `source_geography`, `sa2_code FK`, `mapping_basis`, `source_id FK`; unique alias/source-area/SA2 relationship. Alias text alone is NOT unique across all matches. |
| `indicator` | `indicator_key TEXT PK`, `label`, `unit`, `explanation`; keys: `rent_weekly`, `transport_access`, `population_growth`, `green_space_per_resident`. |
| `area_indicator` | composite PK (`sa2_code`, `indicator_key`); `raw_value`, nullable `score`, `rating`, `start_year`, `end_year`, `reference_period`, `method_version`, `quality_status`, `quality_note`, nullable `coverage_fraction`, `geography_type`, `geography_code`. One current observation per indicator/area in each released DB. |
| `population_history` | composite PK (`sa2_code`, `year`); `population`, `source_id FK`; missing population may be null, never manufactured zero. |
| `data_source` | `source_id TEXT PK`, `publisher`, `dataset_name`, `url`, `resource_url`, `licence`, `reference_period`, `boundary_year`, `downloaded_at`, `checksum`, `limitation`. Separate record per source release. |
| `observation_source` | (`sa2_code`, `indicator_key`) composite FK to observation, `source_id FK`, `role`; composite PK across all four fields. Roles can include numerator, denominator, boundary, raw measure. |
| `pipeline_run` | `run_id TEXT PK`, `built_at`, `data_mode`, `method_version`, `source_manifest_hash`, `validation_status`, `boundary_year`, `population_start_year`, `population_end_year`. |

Enable foreign keys on every relevant connection. Index area names, alias search fields and foreign keys. Validate scores in 0-100, coverage in 0-1, nonnegative area/population quantities, allowed statuses and no score when raw data is unavailable. Growth is allowed to be negative.

A view can flatten the four indicators for API efficiency, but both compare/details must use the same underlying observations. Geometries and raw source files need not be shipped with the web app. Keep the database under backend-only deployment files and open it in SQLite read-only mode.

## 5. REST contract proposal

Use the same response models for fixture and real data. The frontend formats numbers but does not recalculate scores. Pin the schema in backend response models and contract examples at the start.

| Request | Response | Validation |
|---|---|---|
| `GET /api/v1/areas?query=...&limit=20` | `{ "areas": [Area], "meta": Meta }` | Proposed limit 1-50; query maximum 100 characters; unknown search returns empty list. |
| `GET /api/v1/compare?sa2=code1,code2` | `{ "areas": [{ "area": Area, "indicators": [IndicatorValue] }], "meta": Meta }` | Two/three unique supported codes, preserve requested order. |
| `GET /api/v1/areas/{sa2_code}` | `{ "area": Area, "indicators": [IndicatorValue], "population_history": [...], "meta": Meta }` | Unknown area returns 404; invalid format returns 422. |
| `GET /api/v1/sources` | `{ "sources": [Source], "meta": Meta }` | Public source metadata, no local file paths or credentials. |
| `GET /health` | `{ "status": "ok", "database": "ready" }` | 503 when not ready; no private diagnostics. |

Suggested `Area`: `sa2_code` string, `name` string, `boundary_year` integer, `geography_type` string (`SA2`), `matched_alias` string/null. Use official real codes from the boundary master, not invented codes assigned to actual suburb names.

Suggested `Meta`: `data_mode`, `data_version` (pipeline run ID), `method_version`, `boundary_year` and `benchmark_count` (valid transport cohort size, null when no scoring).

Suggested `Source`: `source_id`, `publisher`, `dataset_name`, `url`, `reference_period`, `licence`, `limitation`. Include a `sources` array within each indicator so combined-source measures retain both numerator/denominator provenance.

Example `IndicatorValue` shape below uses a fictional source and value solely to illustrate the contract; it is NOT an actual Melbourne observation:

```json
{
  "key": "rent_weekly",
  "label": "Median weekly rent",
  "raw_value": 400,
  "unit": "AUD/week",
  "score": null,
  "rating": null,
  "reference_period": "2021 Census",
  "start_year": 2021,
  "end_year": 2021,
  "geography": {"type": "SA2", "code": "999999991", "boundary_year": 2021},
  "quality": {"status": "available", "reason": null, "coverage_fraction": null},
  "method_version": "draft-1",
  "explanation": "Median weekly rent reported in the 2021 Census; not current advertised rent.",
  "sources": [{
    "source_id": "synthetic-fixture",
    "publisher": "Development team",
    "dataset_name": "Synthetic fixture; not ABS observations",
    "url": null,
    "reference_period": "Example only",
    "licence": null,
    "limitation": "Fictional values for development only"
  }]
}
```

Null is a JSON null, not a string or zero. An unavailable indicator keeps its key/label/unit but sets raw value, score and rating to null and supplies a quality reason. Home needs search results only; static explanatory content does not need an API request. Compare uses the same four indicator objects as details. Population history items contain `year`, `population` and `source_id`, sorted ascending; their sources are available through `/sources`.

Use a consistent error envelope, e.g. `{ "error": { "code": "INVALID_SELECTION", "message": "Choose two or three different areas." } }`. Add matching FastAPI validation exception handling if adopting this shape, because default validation errors differ. Missing an individual indicator does not make the whole comparison fail. Database failure returns a safe 503 and the UI offers retry.

## 6. Mock-to-real integration

Create fixtures for three fictional areas with nine-digit string IDs reserved for development, e.g. `999999991` to `999999993`, and clearly fictional names. Cover normal values, partial data, ties, negative growth and zero-baseline growth in tests. These IDs must not enter the real release.

Use one pipeline entry point accepting either curated synthetic CSVs or validated real CSVs. Use the same schema and API response models in both modes. Seed all four indicator rows even when one is unavailable so the page structure is stable. Mark synthetic mode in metadata and show a development banner.

Before replacing fixtures: verify all real IDs against the official master, validate all joins, inspect sample outputs, reject synthetic source IDs, compare API contract output and rerun the full browser journey. Store DB releases with checksums. Do not use mock data as an automatic fallback when the production API fails.

## 7. Tests that resolve real risks

- Formula examples: population 1000 -> 1100 equals 10%; 1000 -> 900 equals -10%; zero starting population is unavailable; 20000 sqm / 1000 residents equals 20 sqm/person.
- Percentiles: distinct values hit expected endpoints; ties get identical scores; one observation has no score; comparison selection does not change a score.
- Spatial: a polygon crossing an SA2 boundary is split correctly; duplicate park geometry does not double count; uncovered PTAL is not zero; chosen public-access filter is logged.
- Schema: duplicate observation keys rejected; broken foreign keys rejected; null and zero remain distinct; every displayed measure links to source records.
- API/UI: repeated codes and four areas rejected; malformed and unknown codes handled; missing indicators remain visible; compare/details agree; direct links reload; loading and retry work.
- Release: frontend build contains no SQLite file or secrets; runtime DB is read-only; real builds contain no synthetic records; external API errors reveal no SQL, paths or stack traces.
