# ER diagram and schema design notes

This diagram reflects the delivered [SQLite database](yfn.sqlite), not an unimplemented target. It shows selected columns; the [column dictionary](data-dictionary.md) and [SQL DDL](../../pipeline/greater_melbourne_schema.sql) contain the full schema. The editable source is [schema-erd.mmd](schema-erd.mmd).

```mermaid
erDiagram
    direction LR
    dataSources["data_sources"] {
        TEXT source_id PK
        TEXT publisher
        TEXT dataset_name
        TEXT reference_period
        TEXT observation_date "Nullable"
        TEXT licence
    }
    sourceFiles["source_files"] {
        TEXT file_id PK
        TEXT source_id FK
        TEXT resource_url
        TEXT sha256
        TEXT downloaded_at
    }
    areas {
        TEXT sa2_code PK "2021 edition; nine-digit text"
        TEXT name
        INTEGER boundary_year
        TEXT gccsa_code
        INTEGER is_comparable "Project eligibility rule: positive 2025 population"
        REAL calculated_area_m2
        TEXT source_id FK
    }
    indicators {
        TEXT indicator_key PK
        TEXT label
        TEXT unit
    }
    methods {
        TEXT method_id PK
        TEXT approval_status
        TEXT definition
    }
    observations {
        TEXT sa2_code PK, FK
        TEXT indicator_key PK, FK
        REAL raw_value "Nullable"
        REAL score "Nullable; no score is supplied"
        TEXT quality_status
        TEXT quality_note
        REAL coverage_fraction "Nullable; unknown differs from zero"
        TEXT reference_period
        TEXT method_id FK
    }
    populationHistory["population_history"] {
        TEXT sa2_code PK, FK
        INTEGER year PK
        INTEGER population "Nullable; zero preserved"
        TEXT revision_status
        TEXT source_id FK
        TEXT source_locator
    }
    observationSources["observation_sources"] {
        TEXT sa2_code PK, FK
        TEXT indicator_key PK, FK
        TEXT source_id PK, FK
        TEXT role PK
    }
    observationComponents["observation_components"] {
        TEXT sa2_code PK, FK
        TEXT indicator_key PK, FK
        TEXT component_key PK
        REAL value "Nullable"
        TEXT unit
        TEXT reference_period
        TEXT source_id FK
    }
    areaDiagnostics["area_diagnostics"] {
        TEXT sa2_code PK, FK
        REAL ptal_coverage_fraction
        INTEGER park_included_feature_count
        REAL park_union_area_m2
        REAL park_overlap_removed_m2
        REAL open_space_inventory_coverage_fraction "Unknown; null"
    }
    sampleRelease["sample_release"] {
        TEXT release_id PK
        TEXT data_mode "Real"
        INTEGER publication_ready "True"
        TEXT manifest_json "Applies to this whole database file"
    }
    dataSources ||--o{ sourceFiles : contains
    dataSources ||..o{ areas : defines
    areas ||--o{ observations : has
    indicators ||--o{ observations : identifies
    methods ||..o{ observations : calculates
    areas ||--o{ populationHistory : has
    dataSources ||..o{ populationHistory : estimates
    observations ||--o{ observationSources : cites
    dataSources ||--o{ observationSources : supports
    observations ||--o{ observationComponents : derives_from
    dataSources ||..o{ observationComponents : supplies
    areas ||--o| areaDiagnostics : has
```


## Reading the relationships

An area has four observations in this release and six population-history rows. The SQL schema allows any number; the builder validates the required four/six cardinalities. Each observation is uniquely identified by `(sa2_code, indicator_key)`.

An observation can use multiple sources. `observation_sources` joins it to each dataset and records a role such as numerator, denominator or boundary. `observation_components` retains the actual inputs and their periods. For open space, the inventory area and 2025 population are separate components from different sources.

One dataset can have many downloaded files. `source_files` records exact API requests, checksums and retrieval dates, while `data_sources` stores shared meaning and limitations. Intersection audit rows identify source feature IDs and their exact raw file; those large audits and geometry are kept outside the runtime database.

Solid identifying relationships indicate a parent key forms part of a child's primary key; dotted relationships are other foreign keys. Mandatory parent references use `||`; SQL permits zero or more children unless an additional constraint says otherwise. The single diagnostics row per area is enforced by its primary key. The builder supplies one for every area.

`sample_release` describes the whole database file and has no row-level foreign key to the other tables. This is deliberate for one release per file. Do not add a fictitious relationship to the diagram.

## Design decisions supported by the real data

1. **Retain geography independently of indicator availability.** Two SA2s have zero residents. Keep them for traceability while the project eligibility rule excludes them from comparisons that require per-resident measures.
2. **Separate raw input tokens from display values.** Three source rent zeros become unavailable medians; original tokens remain in the audit. Zero population remains a genuine integer zero.
3. **Keep coverage independent of value and quality.** A numeric PTAL average can cover less than 1% of an SA2. Open-space inventory completeness is unknown even when a polygon is present. Both need explicit handling.
4. **Store numerator and denominator.** Large public-open-space ratios can reflect a tiny resident population. The denominator must be inspectable, not hidden behind a rounded ratio.
5. **Version methods and dates.** A 2021 rent, a 2020–2025 population change and an undated inventory must not share a fabricated single observation date. A transport raw index and its future percentile are separate fields.

## Boundaries of this schema example

The database stores one boundary edition and one current observation per area/indicator per release. For multiple boundary editions or observation releases in one database, extend the primary and foreign keys consistently (for example with a geography-edition identity and release ID). Do not merely add a year column while keeping an incompatible unique key.

The release metadata records real data that the team has approved for publication (`publication_ready=1`). `is_comparable` currently means positive 2025 ERP and does not approve transport scoring eligibility or a minimum population threshold. Source quality cannot be fixed by a database constraint.

No suburb-alias table is populated because a verified one-to-many suburb/SA2 mapping has not been acquired. The diagram does not invent one. The application can begin with official SA2 names, and a future alias relationship can be added with its own source and mapping basis.
