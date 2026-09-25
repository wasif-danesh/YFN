# Frontend

Nuxt 4, Vue, JavaScript, Tailwind and Leaflet power **Your Friendly Neighbourhood**.

| Route | Purpose |
|---|---|
| `/` | Renter homepage: select two or three areas through typeahead and the interactive Greater Melbourne map |
| `/compare?sa2=206041117,213031348` | Comparison: one selected area can be inspected while adding a second; up to three areas, dated values, nulls and source notes |
| `/areas/206041117` | Area Details: four indicators, annual population chart/table and source notes; optional `compare` query preserves the selected areas |
| `/api-test-console` | Preserved developer console: four API requests, raw JSON, HTTP status and retry controls |

Home follows the approved blue design, using verified ABS boundaries and allowing two or three areas to be combined from search and map selections before comparison. Compare and Area Details complete the renter journey with dated measures, rent differences, population history and selection-preserving return navigation. The site is published and open to search engines; only the API console is `noindex`.

## Run locally

For the complete first-time and daily two-terminal workflow, follow [Local application development](../README.md#local-application-development). Install the Node version in `.nvmrc`. From the repository root, start the [backend](../backend/README.md) in one terminal. In a second terminal:

```sh
# First setup only; do not overwrite an existing .env.
cp frontend/.env.example frontend/.env
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open `http://localhost:3000`. On PowerShell, use `Copy-Item` instead of `cp`. The default API is `http://localhost:8000/api/v1`; the backend example allows the localhost frontend origin. Use the same hostname consistently because `localhost` and `127.0.0.1` are distinct browser origins.

## Files

| File | Responsibility |
|---|---|
| `app/pages/index.vue` | Renter homepage and ordered two-to-three-area selection |
| `app/pages/compare.vue` | URL selection, comparison requests, values and source notes |
| `app/pages/areas/[sa2_code].vue` | Dynamic area details, request states and comparison return link |
| `app/components/ComparisonTable.vue`, `IndicatorValue.vue` | Shared measure presentation, bars, notes, null flags and source notes |
| `app/components/PopulationHistory.vue` | Population chart, accessible table and revision status |
| `app/utils/comparison.js`, `population.js` | Rent difference rules and population chart calculations |
| `app/pages/api-test-console.vue` | Preserved diagnostic page |
| `app/components/AreaSearch.vue` | Debounced search, keyboard selection, loading/retry and stale-response protection |
| `app/components/AreaMap.client.vue` | Client-only Leaflet map, area selection, reset and tile failure handling |
| `app/components/SiteHeader.vue`, `SiteFooter.vue`, `SiteIcon.vue` | Shared renter navigation and icons |
| `app/components/ApiConsole.vue` | Inputs, four request cards, status and retry UI |
| `app/utils/api.js` | Endpoint URLs, fetch handling and 90-second timeout |
| `app/assets/css/main.css`, `renter.css` | Console styles and responsive renter theme |
| `public/maps/` | Display-only GeoJSON and source/processing provenance |
| `nuxt.config.js` | Static generation, Tailwind and public configuration |
| `tests/unit/` | URL, HTTP, timeout, component and retry checks |
| `tests/e2e/` | Desktop/mobile browser checks using the real SQLite-backed API |

API calls run after the page mounts in the browser, so static generation does not require a running API. JSON is rendered as escaped text. The console is marked `noindex`; it has no authentication and will be publicly accessible when deployed.

## Tests

From the repository root:

```sh
npm --prefix frontend test
npm --prefix frontend run generate
```

For browser tests, first install backend runtime dependencies in the activated Python environment, then install Chromium once:

```sh
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
npx --prefix frontend playwright install chromium
npm --prefix frontend run test:e2e
```

On Windows activate with `.venv\Scripts\Activate.ps1`. Stop any existing server on ports 8000 or 4173 before browser tests: Playwright starts and stops its own API and static preview server. Generate the site with the default local API URL for these tests. The tests exercise the console, combined keyboard-search/map selection on Home, two-to-three-area comparison, removal, direct-link reload, population history, return navigation, unavailable values, invalid selection and map failure on desktop and mobile. Street tiles are deliberately blocked in automated journey tests to avoid depending on a third-party service; real boundary data and API responses are used. Screenshots and failure traces are saved under ignored `frontend/test-results/`.

To inspect the generated build manually, run `npm --prefix frontend run preview` and open `http://127.0.0.1:4173`. Add that exact origin to the local backend CORS allowlist and restart the API first. The preview server is for local testing; Render hosts the generated files directly.

CI installs dependencies from the lockfile, runs unit tests, generates the site, checks that no database/backend files are published, and runs browser tests. Browser tests cover the complete renter journey, preserved comparison selection after a detail-page reload, API recovery, missing rent and unknown areas.

## Deployment configuration

See [Render setup](../deploy/README.md). The Blueprint sets `NUXT_PUBLIC_API_ORIGIN` from the API service's public Render URL; Nuxt appends `/api/v1`. Optional `NUXT_PUBLIC_API_BASE` overrides that with a complete URL. Changing either requires a static-site rebuild. Never put secrets, SQLite or raw datasets in `public/` or public Nuxt configuration.

## Browser service check

The frontend uses `/api/v1/status` for its Service health card. `/health` remains available for Render’s configured health check. Both routes run the same database readiness handler and return the same JSON and error responses. This change avoids the observed browser-profile block on `/health`; it cannot guarantee compatibility with every extension. Deploy the backend with the new route before deploying the frontend, then retry in the affected regular browser profile.

## Homepage map data

`public/maps/greater-melbourne-sa2.geojson` contains all 361 spatial Greater Melbourne SA2s, joined by exact code and name to the maintained database. Two zero-population areas are shown but cannot be compared. The map is a display asset, not a second statistics database.

The pipeline owner can rebuild it from the existing verified ABS ZIP with:

```sh
python pipeline/build_homepage_map.py
python scripts/check_homepage_map.py
```

Use the pipeline environment/dependencies described in the root README for the build. The check uses only Python’s standard library and runs in CI. Rebuild the map whenever boundary identities or comparison eligibility change. Commit GeoJSON and `provenance.json` together. The builder checks the downloaded source hash, exact database joins and polygon validity, simplifies shared edges with Shapely coverage simplification in EPSG:7855 (30-metre tolerance), then transforms to EPSG:4326. Never use this simplified geometry to calculate indicators.

Leaflet loads the committed polygons in the browser and requests street tiles directly from OpenStreetMap. No Google Maps key is needed. Visible attribution is retained; tile requests use normal browser caching and a Referer, with no bulk/offline downloads. Search and boundaries remain available if tiles fail. Review the [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/) before substantially increasing traffic or adding offline use. Boundary source attribution and the CC BY 4.0 licence are recorded in `public/maps/provenance.json`.

## Verification — 9 September 2026

The homepage change passed 13 frontend unit/component tests, 6 desktop/mobile browser tests, static generation, and database/map integrity checks. Live OpenStreetMap tiles were also reviewed on desktop and mobile with no browser page errors or page-wide horizontal overflow. Tests verify boundary selection and search still work when tiles are blocked. The map asset contains 361 valid matched polygons with shared topology preserved by the builder. These are local checks, not evidence that the new pages have been deployed.

## Compare and Area Details behaviour

Home collects two or three distinct eligible SA2s and passes their ordered codes to Compare. Compare also accepts one starting area for compatible direct links. The ordered selection lives in the `sa2` query parameter. Detail links carry that selection in `compare`; Back to comparison restores it. No session storage or additional database is needed. Dynamic detail URLs use the existing Render rewrite to `/200.html`, including direct visits and reloads.

Rent differences use only available observations with matching units, reference periods and methods. They describe historical Census rent, not current prices or predicted savings. Population charts use the API’s actual annual observations, break lines across missing years and show revision status in a table. Unknown values stay unavailable. No overall score or ranking is added.

The completed pages pass 34 unit/component tests, 10 desktop/mobile browser tests and static generation locally. The tests use the maintained, publication-ready SQLite release; missing-data fixtures are intercepted only inside tests. Passing checks confirm expected application behaviour but do not remove the source dates, coverage constraints or limitations shown to users.
