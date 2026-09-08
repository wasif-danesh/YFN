# Requirements and delivery plan

Status: consolidated development draft, 8 September 2026. Read `project-context.md` for the source conflicts and pending decisions.

## User journey

Home: understand purpose and search an area -> Compare: select two or three areas and inspect trade-offs -> Area Details: inspect one area's indicators and population history -> return to the same comparison.

## Iteration 1 target

Deliver the three wireframe pages with four indicator categories, a REST API, reproducible SQLite build and a complete deployed journey. The later draft specification targets all four categories; the older pitch has a narrower minimum. Resolve this scope difference at the start. Development with synthetic data is a staging milestone, not proof that the final data requirement is satisfied.

| ID | Behaviour | Acceptance condition |
|---|---|---|
| H1 | Home shows project name, renter-focused purpose and search | Matches home wireframe structure; no planner language |
| H2 | Search partial area name and choose a result | Case-insensitive; distinct official identities; keyboard-operable results; empty state |
| H3 | Start comparison | Selected area transfers; prompt to add another until at least two are selected |
| H4 | Four category cards | Icon and title on the first row, short description underneath; no SDG badges |
| C1 | Add/remove comparison areas | Two or three unique eligible SA2s; duplicates and a fourth selection prevented |
| C2 | Compare four measures | Rent, transport, growth and green space appear in the same order and units |
| C3 | Explain meaning | Concise What it means text; explicit years and any material coverage limitation |
| C4 | Missing and limited results | Not available for null; zero only when measured; limited result has an explanation |
| C5 | Continue to details | Correct area opens; selected comparison is preserved |
| D1 | Area identity | Official area name and brief SA2/suburb caveat |
| D2 | Four indicator cards | Raw/display value, unit, reference period, source and short explanation; only transport needs proposed rating |
| D3 | Population history | Real calendar years and values; accessible table or text equivalent; missing years stay gaps |
| D4 | Return/recompare | Back preserves selection; another-area action returns to selection |
| X1 | Loading and failure | All data views handle loading, API unavailable, retry, unknown area and partial data |
| X2 | Direct links | Compare and details reload correctly on static hosting; URL selection is validated |

## Wireframe corrections to apply in implementation

- Image numbers such as $480, $520, 72/100, 84/100, 6.4% and 18 m2 are illustrative; never seed real named areas with them as factual values.
- Replace 'Typical advertised or reported rent' with the exact meaning of the selected source. For Census 2021: 'Median weekly rent reported in the 2021 Census.' Show 2021 next to the amount.
- Replace 'latest available year' and 'Year 1' chart labels with actual source years.
- A 2020-2025 five-year change needs endpoints five years apart and six annual observations when complete.
- Rating labels must be computed consistently. The compare mock labels both 72 and 84 'Stronger access', whereas v1.0 proposes different bands. Do not reproduce contradictory labels.
- Area-wide open-space provision is not a guarantee of walking access from a rental property. Correct any wording that implies that.
- Population change describes an area trend; it does not establish service shortages or predict future rents.
- Source information may use small notes, expandable details or supporting links. No standalone methodology section is requested.

## Iteration 2 candidate scope

Prioritise the same renter journey using feedback. These are candidates, not a commitment to implement all of them:

1. Improve suburb alias matching and ambiguous-area choices.
2. Improve mobile comparison, keyboard navigation and clarity of explanations.
3. Address data coverage gaps and refresh older source releases where defensible.
4. Evaluate a newer suburb rent dataset without misrepresenting it as SA2 rent.
5. Improve provenance, automated data validation and release recovery.
6. Add aggregate analytics only after agreeing a useful measurement and a privacy-preserving configuration; analytics is not needed to build the core journey.

Plan storage for source versions and observations now so these changes do not require a replacement schema. Do not promise unvalidated new measures.

## Parallel development

| Workstream | Can start immediately with | Delivers |
|---|---|---|
| Frontend | Wireframes and shared synthetic JSON examples | Three pages, loading/error states, one API client module |
| API | Agreed response models and seeded SQLite | Search, compare, details, sources and health endpoints |
| Data | Source manifest and expected curated columns | Profile reports, cleansed tables, real data, validation evidence |
| Integration/QA | Same schema and contracts | Database builder, automated checks, Render configuration, end-to-end tests |

Assign owners in the team meeting; this table does not assign names. Use mock and real data through the same database builder and API models. Avoid separate hard-coded UI calculations. Backend/QA and data owners jointly review schema changes.

## Suggested two-week schedule

- Days 1-2: agree scope, inspect all data sources, settle response contract, seed synthetic SQLite, deploy the first minimal frontend/API connection if deployment is authorised.
- Days 3-5: complete the three-page synthetic-data journey while validating a small real-data slice, including spatial sources.
- Days 6-8: integrate real curated data through the same loader; resolve calculation and coverage issues; scale across the eligible area set.
- Days 9-10: complete functional, data, accessibility and security checks; conduct user tests; resolve critical issues.
- Days 11-14: keep contingency time for source problems, fixes, release checks, documentation and demonstration rehearsal.

These are elapsed-day planning targets, not a guarantee of effort. Do not leave the first real-data integration until the last two days. If source feasibility fails, surface the affected feature and seek a scope decision early.

## Proposed coordination

Use Trello for scope, acceptance criteria, task owners, progress and test evidence. A short asynchronous stand-up on agreed working days can report completed work, next work and blockers. Weekly calls can handle demonstrations and decisions. Review whether this reduces or adds communication overhead at the retrospective; it is a proposal, not evidence the team already uses it.

## Quality and definition of done

- Usability: a representative renter can complete the journey and explain at least one trade-off; record the test results rather than claiming success in advance.
- Accessibility: target WCAG 2.2 AA; labelled controls, keyboard operation, focus visibility, contrast, semantic comparison tables and text equivalents for charts. Combine automated checks with manual testing.
- Security: HTTPS, validated bounded inputs, parameterised SELECTs, read-only runtime database, safe errors, no secrets in frontend/Git, appropriate response headers and dependency checks. CORS is a browser policy, not API authentication. A public read-only API is expected.
- Privacy: no account or personal-data forms; no profiling by default. Review infrastructure logs and any analytics before making claims about retention.
- Performance: bounded search results and compact responses; index lookup columns. Proposed warm API response target is under one second on the agreed test dataset; measure and report hosting cold starts separately.
- SEO: meaningful static home content and page metadata; no need to index every compare combination. Decide whether area pages are prerendered during implementation; client-fetched JSON alone does not guarantee indexable content.
- Data: source manifest, compatible geography, tested formulas, null/suppression handling, provenance and successful reproducible database build.
- Release: no silent fixture fallback, working static routes, successful health check, deployed full journey, evidence in Trello and recovery instructions.

An unavailable value is correct for a genuine data gap. It is not a substitute for completing an entire promised data pipeline. Confirm any feature deferral against the assessment and team agreement.

## Deployment proposal

Configure two services from one GitHub repository: `frontend/` as a Render Static Site and `backend/` as a Render Python Web Service. Frontend builds generate static assets; Node.js is not required as a live frontend server for this architecture. FastAPI reads a packaged SQLite release built before deployment. The processing pipeline does not run inside user requests.

Set the frontend's public API URL and backend's allowed frontend origin through configuration. The API URL is public, not a secret. Keep the database outside the static site's published directory. Use a build/release step to place the validated database with the backend; do not depend on runtime writes or a persistent disk.

Verify current Render plan limits, cold-start behaviour, build/output commands and route handling at implementation time. Run GitHub checks before release and configure the chosen deployment mechanism to respect their result; automatic deploy-on-push alone does not establish this. Do not commit credentials or deploy hooks. Prepare deployment configuration as code and use the user's deployment authorisation before publishing.
