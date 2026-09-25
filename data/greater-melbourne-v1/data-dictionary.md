# Database column dictionary

Generated from the delivered SQLite schema. See [executable SQL](../../pipeline/greater_melbourne_schema.sql) for all CHECK constraints and view definitions. Identifiers are text. Blank numeric CSV cells load as SQL NULL.

## `areas`

One spatial 2021 Greater Melbourne SA2 per row, with identity and project comparison eligibility.

Rows: 361.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1 |
| `name` | TEXT | No |  |
| `boundary_year` | INTEGER | No |  |
| `gccsa_code` | TEXT | No |  |
| `official_area_sq_km` | REAL | No |  |
| `calculated_area_m2` | REAL | No |  |
| `area_crs` | TEXT | No |  |
| `is_comparable` | INTEGER | No |  |
| `eligibility_note` | TEXT | No |  |
| `source_id` | TEXT | No | FK → data_sources primary key |

## `indicators`

Four reusable measure labels and units.

Rows: 4.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `indicator_key` | TEXT | No | PK position 1 |
| `label` | TEXT | No |  |
| `unit` | TEXT | No |  |

## `methods`

Versioned calculation definitions and their approval status.

Rows: 4.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `method_id` | TEXT | No | PK position 1 |
| `approval_status` | TEXT | No |  |
| `definition` | TEXT | No |  |

## `observations`

One current measure per area/indicator in this database release; value, quality, period and method.

Rows: 1444.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1; FK → areas primary key |
| `indicator_key` | TEXT | No | PK position 2; FK → indicators primary key |
| `raw_value` | REAL | Yes |  |
| `score` | REAL | Yes |  |
| `rating` | TEXT | Yes |  |
| `reference_period` | TEXT | No |  |
| `start_year` | INTEGER | Yes |  |
| `end_year` | INTEGER | Yes |  |
| `quality_status` | TEXT | No |  |
| `quality_note` | TEXT | No |  |
| `coverage_fraction` | REAL | Yes |  |
| `method_id` | TEXT | No | FK → methods primary key |

## `population_history`

Six annual population observations per SA2, with revision status and original workbook cell.

Rows: 2166.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1; FK → areas primary key |
| `year` | INTEGER | No | PK position 2 |
| `population` | INTEGER | Yes |  |
| `reference_date` | TEXT | No |  |
| `revision_status` | TEXT | No |  |
| `source_id` | TEXT | No | FK → data_sources primary key |
| `source_locator` | TEXT | No |  |

## `data_sources`

One dataset/release per source; publisher, period, licence and limitations.

Rows: 5.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `source_id` | TEXT | No | PK position 1 |
| `publisher` | TEXT | No |  |
| `dataset_name` | TEXT | No |  |
| `url` | TEXT | No |  |
| `reference_period` | TEXT | No |  |
| `boundary_year` | INTEGER | Yes |  |
| `observation_date` | TEXT | Yes |  |
| `licence` | TEXT | No |  |
| `limitation` | TEXT | No |  |

## `source_files`

Several original files or API responses per source; exact URLs and hashes.

Rows: 178.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `file_id` | TEXT | No | PK position 1 |
| `source_id` | TEXT | No | FK → data_sources primary key |
| `path` | TEXT | No |  |
| `resource_url` | TEXT | No |  |
| `sha256` | TEXT | No |  |
| `downloaded_at` | TEXT | No |  |
| `bytes` | INTEGER | No |  |

## `observation_sources`

Many-to-many provenance with the source role in each observation.

Rows: 3249.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1; FK → observations primary key |
| `indicator_key` | TEXT | No | PK position 2; FK → observations primary key |
| `source_id` | TEXT | No | PK position 3; FK → data_sources primary key |
| `role` | TEXT | No | PK position 4 |

## `observation_components`

Numerators, denominators and transport-weight components with their own source and period.

Rows: 2527.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1; FK → observations primary key |
| `indicator_key` | TEXT | No | PK position 2; FK → observations primary key |
| `component_key` | TEXT | No | PK position 3 |
| `value` | REAL | Yes |  |
| `unit` | TEXT | No |  |
| `reference_period` | TEXT | No |  |
| `source_id` | TEXT | No | FK → data_sources primary key |

## `area_diagnostics`

Spatial coverage, inventory area, overlap and water-filter sensitivity; unknown coverage stays null.

Rows: 361.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `sa2_code` | TEXT | No | PK position 1; FK → areas primary key |
| `ptal_candidate_count` | INTEGER | No |  |
| `ptal_intersecting_count` | INTEGER | No |  |
| `ptal_valid_count` | INTEGER | No |  |
| `ptal_valid_covered_area_m2` | REAL | No |  |
| `ptal_coverage_fraction` | REAL | No |  |
| `park_candidate_count` | INTEGER | No |  |
| `park_included_feature_count` | INTEGER | No |  |
| `park_union_area_m2` | REAL | No |  |
| `park_overlap_removed_m2` | REAL | No |  |
| `selected_space_excluding_explicit_water_body_yes_m2_per_person` | REAL | Yes |  |
| `open_space_inventory_coverage_fraction` | REAL | Yes |  |

## `sample_release`

Metadata for the entire SQLite file; one release, real data and publication_ready=1.

Rows: 1.

| Column | SQLite type | Nullable | Key |
|---|---|---|---|
| `release_id` | TEXT | No | PK position 1 |
| `data_mode` | TEXT | No |  |
| `publication_ready` | INTEGER | No |  |
| `manifest_json` | TEXT | No |  |

## `v_area_summary` view

One row per SA2, with four raw measures, comparison eligibility, quality statuses and transport coverage. Join observations for quality notes, periods and sources before presenting the values to renters.

Columns: `sa2_code`, `name`, `boundary_year`, `is_comparable`, `rent_2021_aud_week`, `population_growth_percent`, `transport_raw_index_sample`, `selected_open_space_m2_per_person_sample`, `rent_quality`, `population_growth_quality`, `transport_quality`, `transport_coverage_fraction`, `open_space_quality`.
