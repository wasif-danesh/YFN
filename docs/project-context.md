# Project context and decision record

Prepared: 8 September 2026. Status: development handover for team review.

## Purpose and audience

**Your Friendly Neighbourhood** helps renters unfamiliar with Melbourne compare potential areas before investigating where to live. Priority groups include new immigrants, international students and interstate migrants. The problem is fragmented housing, transport, population and open-space information that is difficult to compare consistently.

The website supports SDG 11, Sustainable Cities and Communities. The housing, transport, population and green-space measures relate to themes in targets 11.1, 11.2, 11.3 and 11.7; they are not official UN indicator measurements.

Team members listed in the proposal: Andrew Tran, Sanskrita DSarma, Tin Nguyen and Wasif Danesh. Current development responsibilities have not been assigned in this handover.

## Established direction from the conversation

| Decision | Current direction |
|---|---|
| Name and primary user | Your Friendly Neighbourhood; renters unfamiliar with Melbourne |
| Page structure | Home, Compare, Area Details; latest renter wireframes supplied |
| Comparison | Two or three areas; consistent measures; clear trade-offs |
| Measures shown in wireframes | Median weekly rent, relative transport access, actual recent population growth, green space per resident |
| Population outlook | Historical observed/estimated population change; no ML forecast |
| Main UI | Simple language; no methodology section; brief evidence and limitations remain available |
| Map | Not required; excluded from the current implementation baseline |
| Privacy | No login, personal profiles or retention of personal information |
| Architecture | Static Nuxt/Vue frontend; FastAPI; Python pipeline; SQLite; Render; GitHub |
| Database | Prepared offline and read-only in the running API |
| Hosting | Render; user reports OLA confirmed there is no Monash development environment |
| Delivery constraint | Approximately two weeks for Iteration 1 development, four-person team |
| Parallel development | User proposes UI/API/database development with mock data alongside real-data preparation; this handover provides a contract-based plan |

## Superseded or unapproved ideas

- UrbanLens Melbourne and community-infrastructure planners are superseded.
- AccessReady Melbourne was a different earlier idea; do not import its wheelchair-destination functionality.
- ML growth forecasts, an overall liveability ranking, Redis and Monash hosting are outside the current baseline.
- No decision has been made to introduce maps, property listings, personal affordability advice, accounts or saved profiles.
- Earlier discussions of cloud alternatives do not change the current choice of Render.

## Geography

The proposal and later specification use Greater Melbourne SA2s. The 7 September discussion recommended retaining SA2 for Iteration 1 while making suburb search more familiar. The user has not explicitly approved a full change to suburb geography or the additional mapping feature.

Working baseline: 2021 SA2 edition, matched to source geography. Validate the edition of every actual downloaded release. Start with case-insensitive SA2 name search. Add verified suburb aliases if feasible; retain one-to-many matches rather than assigning a suburb silently to one SA2. Never describe all SA2 results as exact whole-suburb statistics.

No visible map is necessary for spatial processing: boundary polygons are used offline to assign or intersect transport/open-space data to the comparison areas.

## Differences between source documents

| Topic | Earlier material | Later direction and handling |
|---|---|---|
| Iteration 1 | Pitch section 10 promises population and housing | Specification v1.0 and user emphasis on wireframes target all four indicators. Plan all four, but confirm release scope and data feasibility immediately. Do not silently drop two categories. |
| Ratings | Pitch proposes pressure percentiles across multiple categories | v1.0 uses raw rent, raw growth, raw green space and a transport score. Use that simpler proposal for development; production scoring still needs validation. |
| Housing | Pitch discusses rent relative to income | Wireframes and v1.0 display median weekly rent. Do not add a rent-to-income score without a new agreed definition. |
| Sequence | v1.0 suggests pipeline before full API integration | User later proposes parallel UI/API/database development with mocks. Use shared contracts and integrate real data early. |
| Search | v1.0 delays aliases until Iteration 2 | Latest recommendation suggests renter-friendly suburb search. Treat aliases as an explicit decision, not already completed mapping. |
| Navigation | Images contain Data/How it works links | Provide lightweight supporting information if needed. Do not create a methodology page merely because older images mention it. |

## Decisions to resolve at the beginning

1. Confirm all-four-indicator Iteration 1 release scope versus the narrower pitch commitment; agree a fallback with the team/OLA if spatial data is not usable in time.
2. Confirm SA2 baseline and whether suburb aliases are Iteration 1 or Iteration 2.
3. Validate the actual source files, licences, geographic editions, reference years, required field names and coverage.
4. Confirm housing is dated Census rent for Iteration 1. A newer suburb rental source is a separate enhancement requiring geographic review.
5. Confirm population start/end years after inspecting the annual ERP release; 2020-2025 is proposed, not yet verified in this handover.
6. Validate PTAL units, whether numeric averaging is defensible, coverage criteria, score method and wording.
7. Approve the public open-space category filter and population denominator year.
8. Agree schema/JSON contract with the four workstreams and assign responsibilities.

UI scaffolding, synthetic fixtures, API validation and database build tooling can proceed while source-specific decisions are resolved. Real-data publication depends on resolving the affected definitions.

## What this handover does not establish

Subsequent evidence, 8 September 2026: the user requested a verified sample to help design the database. The [four-area regression evidence](../pipeline/fixtures/four-area-regression.json) covers Carlton, Footscray, Clayton - Central and Clayton (North) - Notting Hill. It validates exact 2021 SA2 joins, Census rent, the proposed 2020–2025 ERP window and sample spatial calculations. No simple "Clayton" SA2 exists in the chosen edition. All four sample areas have effectively complete PTAL polygon coverage, but a Melbourne-wide eligibility threshold and percentile remain unapproved. The open-space inventory date/completeness remains unknown; water flags materially affect Footscray's result. This is real input data with provisional spatial methods, not an approved final assessment release.

The original handover did not certify downloaded data, implemented code, actual hosting availability or current prices. Subsequent sample evidence is limited to the scope above and does not establish full-Melbourne production readiness. Research figures in the copied proposal have not all been reverified. Latest team approval, OLA feedback and new artefacts supplied after this date should be recorded here. Preserve source documents as evidence instead of quietly rewriting them.

## Greater Melbourne sample requested by the user

On 8 September 2026 the user explicitly requested extending the real-data sample across all Greater Melbourne SA2s for schema and ER-diagram design. The [complete-area package](../data/greater-melbourne-v1/README.md) contains all 361 spatial ASGS 2021 `2GMEL` SA2s, 1,444 indicator rows and 2,166 annual population records, together with an executable schema and ER diagram. The original four-area package was retired on 9 September; compact regression values are retained in the pipeline fixtures.

This establishes source-backed availability and calculations for the documented sample methods, with explicit gaps: 358 rent values, 359 population changes, 360 raw transport values and 354 selected-open-space ratios. All spatial results remain provisional/limited. Two zero-population SA2s are retained but marked outside the sample comparison set. Three zero rent tokens are unavailable medians, and outer-area PTAL coverage can be very small. Six annual population sums reconcile exactly to ABS Greater Melbourne totals. Production scoring, coverage eligibility and the public-open-space filter remain decisions for the team; no public release or deployment was authorised by this data request.

## Development repository guide

The user requested a professional team README and folder structure accounting for GitHub-triggered Render deployment. The root [README](../README.md) now documents the recommended monorepo layout, clone/local workflows, current data and planned application commands. Workspace guides, environment examples, a clean-clone data check and initial data-only GitHub CI are present. [The Render template](../deploy/render.yaml.example) remains inactive until the applications, required application checks and approved runtime data are implemented. It uses repository-root build contexts for access to shared data and contracts, path filters, and deployment after CI checks pass on the proposed `main` branch. This does not create a GitHub repository or authorize an external deployment.

## Single-database simplification — 9 September 2026

The user approved one maintained directory, `data/greater-melbourne-v1/`, and one database, `yfn.sqlite`. There are no samples or releases subfolders and no copy/promotion step for the backend. Local and Render configuration use the same repository-relative database path. Frontend pages consume JSON from FastAPI, not SQLite directly. Raw inputs stay local and ignored; curated data, provenance and compact validation evidence remain committed. Git history supports rollback. Data changes are rebuilt and checked before deployment; runtime access remains read-only. The user subsequently approved renaming the database to `yfn.sqlite`. The name identifies the project; publication status and provisional methods remain recorded in metadata.

The four-area package and its acquisition/build scripts are retired. Independent expected values remain as a small regression fixture. The Greater Melbourne pipeline downloads directly and uses shared configuration/calculation modules. This replaces earlier advice requiring separate sample and release databases or parallel synthetic database development. Tests may use temporary in-memory fixtures.

Previously approved UI direction: all four indicator categories in Iteration 1, homepage SA2 typeahead and Leaflet map, and a professional responsive blue theme. Semantic search is excluded. Suburb aliases and sorting/filtering are Iteration 2 candidates; their mockup does not establish verified suburb mappings.
