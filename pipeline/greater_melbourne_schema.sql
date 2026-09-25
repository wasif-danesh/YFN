PRAGMA foreign_keys = ON;
CREATE TABLE data_sources (
 source_id TEXT PRIMARY KEY, publisher TEXT NOT NULL, dataset_name TEXT NOT NULL,
 url TEXT NOT NULL, reference_period TEXT NOT NULL, boundary_year INTEGER,
 observation_date TEXT, licence TEXT NOT NULL, limitation TEXT NOT NULL
) STRICT;
CREATE TABLE source_files (
 file_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES data_sources,
 path TEXT NOT NULL, resource_url TEXT NOT NULL, sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 downloaded_at TEXT NOT NULL, bytes INTEGER NOT NULL CHECK(bytes>0)
) STRICT;
CREATE TABLE methods (
 method_id TEXT PRIMARY KEY, approval_status TEXT NOT NULL CHECK(approval_status IN ('source_definition','approved')),
 definition TEXT NOT NULL
) STRICT;
CREATE TABLE areas (
 sa2_code TEXT PRIMARY KEY CHECK(length(sa2_code)=9 AND sa2_code NOT GLOB '*[^0-9]*'),
 name TEXT NOT NULL, boundary_year INTEGER NOT NULL, gccsa_code TEXT NOT NULL,
 official_area_sq_km REAL NOT NULL CHECK(official_area_sq_km>0),
 calculated_area_m2 REAL NOT NULL CHECK(calculated_area_m2>0), area_crs TEXT NOT NULL,
 is_comparable INTEGER NOT NULL CHECK(is_comparable IN (0,1)), eligibility_note TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES data_sources
) STRICT;
CREATE TABLE indicators (
 indicator_key TEXT PRIMARY KEY, label TEXT NOT NULL, unit TEXT NOT NULL
) STRICT;
CREATE TABLE observations (
 sa2_code TEXT NOT NULL REFERENCES areas, indicator_key TEXT NOT NULL REFERENCES indicators,
 raw_value REAL, score REAL CHECK(score BETWEEN 0 AND 100), rating TEXT,
 reference_period TEXT NOT NULL, start_year INTEGER, end_year INTEGER,
 quality_status TEXT NOT NULL CHECK(quality_status IN ('available','limited','unavailable')),
 quality_note TEXT NOT NULL, coverage_fraction REAL CHECK(coverage_fraction BETWEEN 0 AND 1),
 method_id TEXT NOT NULL REFERENCES methods, PRIMARY KEY(sa2_code,indicator_key),
 CHECK(start_year IS NULL OR end_year IS NULL OR start_year<=end_year),
 CHECK(quality_status!='unavailable' OR (raw_value IS NULL AND score IS NULL AND rating IS NULL)),
 CHECK(quality_status='unavailable' OR raw_value IS NOT NULL),
 CHECK(raw_value IS NOT NULL OR (score IS NULL AND rating IS NULL)),
 CHECK(raw_value IS NULL OR indicator_key='population_growth' OR raw_value>=0)
) STRICT;
CREATE TABLE population_history (
 sa2_code TEXT NOT NULL REFERENCES areas, year INTEGER NOT NULL,
 population INTEGER CHECK(population>=0), reference_date TEXT NOT NULL,
 revision_status TEXT NOT NULL CHECK(revision_status IN ('final','revised','preliminary')),
 source_id TEXT NOT NULL REFERENCES data_sources, source_locator TEXT NOT NULL,
 PRIMARY KEY(sa2_code,year)
) STRICT;
CREATE TABLE observation_sources (
 sa2_code TEXT NOT NULL, indicator_key TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES data_sources, role TEXT NOT NULL,
 PRIMARY KEY(sa2_code,indicator_key,source_id,role),
 FOREIGN KEY(sa2_code,indicator_key) REFERENCES observations
) STRICT;
CREATE TABLE observation_components (
 sa2_code TEXT NOT NULL, indicator_key TEXT NOT NULL, component_key TEXT NOT NULL,
 value REAL, unit TEXT NOT NULL, reference_period TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES data_sources,
 PRIMARY KEY(sa2_code,indicator_key,component_key),
 FOREIGN KEY(sa2_code,indicator_key) REFERENCES observations
) STRICT;
CREATE TABLE sample_release (
 release_id TEXT PRIMARY KEY, data_mode TEXT NOT NULL CHECK(data_mode='real'),
 publication_ready INTEGER NOT NULL CHECK(publication_ready IN (0,1)), manifest_json TEXT NOT NULL
) STRICT;
CREATE TABLE area_diagnostics (
 sa2_code TEXT PRIMARY KEY REFERENCES areas,
 ptal_candidate_count INTEGER NOT NULL CHECK(ptal_candidate_count>=0),
 ptal_intersecting_count INTEGER NOT NULL CHECK(ptal_intersecting_count>=0),
 ptal_valid_count INTEGER NOT NULL CHECK(ptal_valid_count>=0),
 ptal_valid_covered_area_m2 REAL NOT NULL CHECK(ptal_valid_covered_area_m2>=0),
 ptal_coverage_fraction REAL NOT NULL CHECK(ptal_coverage_fraction BETWEEN 0 AND 1),
 park_candidate_count INTEGER NOT NULL CHECK(park_candidate_count>=0),
 park_included_feature_count INTEGER NOT NULL CHECK(park_included_feature_count>=0),
 park_union_area_m2 REAL NOT NULL CHECK(park_union_area_m2>=0),
 park_overlap_removed_m2 REAL NOT NULL CHECK(park_overlap_removed_m2>=0),
 selected_space_excluding_explicit_water_body_yes_m2_per_person REAL,
 open_space_inventory_coverage_fraction REAL CHECK(open_space_inventory_coverage_fraction BETWEEN 0 AND 1)
) STRICT;
CREATE INDEX area_name ON areas(name COLLATE NOCASE);
CREATE INDEX observations_indicator ON observations(indicator_key);
CREATE INDEX sources_by_dataset ON source_files(source_id);
CREATE VIEW v_area_summary AS
 SELECT a.sa2_code,a.name,a.boundary_year,a.is_comparable,
 MAX(CASE WHEN o.indicator_key='rent_weekly' THEN o.raw_value END) rent_2021_aud_week,
 MAX(CASE WHEN o.indicator_key='population_growth' THEN o.raw_value END) population_growth_percent,
 MAX(CASE WHEN o.indicator_key='transport_access' THEN o.raw_value END) transport_raw_index_sample,
 MAX(CASE WHEN o.indicator_key='green_space_per_resident' THEN o.raw_value END) selected_open_space_m2_per_person_sample,
 MAX(CASE WHEN o.indicator_key='rent_weekly' THEN o.quality_status END) rent_quality,
 MAX(CASE WHEN o.indicator_key='population_growth' THEN o.quality_status END) population_growth_quality,
 MAX(CASE WHEN o.indicator_key='transport_access' THEN o.quality_status END) transport_quality,
 MAX(CASE WHEN o.indicator_key='transport_access' THEN o.coverage_fraction END) transport_coverage_fraction,
 MAX(CASE WHEN o.indicator_key='green_space_per_resident' THEN o.quality_status END) open_space_quality
 FROM areas a JOIN observations o USING(sa2_code) GROUP BY a.sa2_code,a.name,a.boundary_year,a.is_comparable;
