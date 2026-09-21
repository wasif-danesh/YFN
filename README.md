# Your Friendly Neighbourhood

**A Greater Melbourne area-comparison website for renters finding their feet in a new city.**

Your Friendly Neighbourhood brings together housing, public transport, population and public open-space information so renters can compare areas and understand the trade-offs. It is designed for newly arrived migrant families settling in Melbourne, who have not yet built up local knowledge of the city.

The application journey is **Home → Compare → Area Details**. Users can compare two or three Statistical Areas Level 2 (SA2s), inspect the underlying measures and see their source dates and limitations. SA2s do not necessarily match suburb boundaries. The project supports the themes of Sustainable Development Goal 11; its measures are not official UN indicators.

## Project status

| Component | Current state |
|---|---|
| Assessment documents and wireframes | Maintained separately in the PGP; not required to build or run this repository |
| Real development data | Prepared for all **361 Greater Melbourne SA2s**, using 2021 boundaries |
| SQLite, schema and ER diagram | Built and verified; **1,444 indicator rows** and **2,166 population-history rows** |
| Data pipeline | Acquisition, offline processing and validation scripts implemented |
| REST API | FastAPI implemented with four browser endpoints plus a hosting health check, response models and backend tests |
| Frontend | Home with typeahead/Leaflet map, full Compare and Area Details, a staged loading message while the free API wakes, plus a separate API test console implemented |
| GitHub checks | Database, backend, frontend unit/build and desktop/mobile browser checks configured |
| Render | Deployed on the free plan: [website](https://yfn-web.onrender.com/) and [API](https://yfn-api.onrender.com/api/v1/status); see the Render guide |

The real dataset is suitable for development and schema design. Transport aggregation, coverage eligibility and the open-space filter remain provisional. `publication_ready=false` is preserved. Application development can proceed while the team resolves these definitions.

The repository is at [github.com/wasif-danesh/YFN](https://github.com/wasif-danesh/YFN). The application is deployed on Render's free plan: the website is at [yfn-web.onrender.com](https://yfn-web.onrender.com/) and the API at [yfn-api.onrender.com](https://yfn-api.onrender.com/api/v1/status).

## Simple team workflow

There is one database: [`data/greater-melbourne-v1/yfn.sqlite`](data/greater-melbourne-v1/yfn.sqlite).

1. Clone/pull the repository and run `python scripts/check_sample.py`.
2. Backend developers use the database path in `backend/.env.example`. Frontend developers call the API; they do not open SQLite.
3. Only the data maintainer runs the acquisition/build commands. They commit the updated database, curated files, manifest and validation evidence together after checks pass.

Local development and Render use the same database path. There are no `samples/` or `releases/` folders, no database selection step and no routine downloads for UI/API developers. The test console labels provisional data explicitly. The final renter release still requires resolving the documented methods.

## Contents

- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Clone and verify the project](#clone-and-verify-the-project)
- [Local application development](#local-application-development)
- [Database and API contract](#database-and-api-contract)
- [Open datasets](#open-datasets)
- [Data preparation and refreshes](#data-preparation-and-refreshes)
- [Team Git workflow](#team-git-workflow)
- [Deploying to Render](#deploying-to-render)
- [Testing and troubleshooting](#testing-and-troubleshooting)
- [Project documentation and responsibilities](#project-documentation-and-responsibilities)
- [Licence](#licence)

## Architecture

Use one repository for the frontend, REST service, data pipeline and shared contracts. Deploy two services from that repository.

```text
Official open datasets
         │ acquisition, cleansing and spatial aggregation
         ▼
Python data pipeline ──► curated CSVs ──► validated SQLite release
                                                │ read-only queries
                                                ▼
                                      FastAPI REST service
                                                │ HTTPS / JSON
                                                ▼
                                      Nuxt / Vue static site
                                                │
                                                ▼
                                             Renters

GitHub feature branch → pull request → checks + review → main
                                                         │
                                               Render build filters
                                                 ┌───────┴───────┐
                                              API service    Static site
```

| Layer | Technology and responsibility |
|---|---|
| Frontend | JavaScript, Vue, Nuxt and Tailwind; renders the three-page journey and handles loading, errors and missing values |
| REST service | Python FastAPI; validates requests, queries SQLite and returns consistent JSON |
| Database | SQLite, constructed offline and opened read-only by the API |
| Data pipeline | Python, Shapely, PyProj, PyShp and OpenPyXL; acquires sources and calculates curated observations |
| Delivery | GitHub pull requests and CI; Render Static Site plus Render Python Web Service |

Node.js is used for frontend tooling and static generation. It is not a separate live application server. Spatial processing runs offline, outside API requests and ordinary Render application builds. The browser accesses the REST API, never SQLite directly.

The initial scope does not include accounts, semantic search, property listings, ML forecasts, Redis or an overall best-neighbourhood score.

## Repository structure

The application workspaces are implemented. Home contains the renter experience, Compare supports two or three areas, Area Details displays indicators and annual population history, and `/api-test-console` preserves the diagnostic page.

```text
yfn/
├── README.md                         # Team onboarding and operating guide
├── LICENSE                           # MIT licence for project software
├── .editorconfig                     # Shared text conventions
├── .gitignore                        # Environments, secrets and bulky outputs
├── .gitattributes                    # Stable line endings for checksummed files
├── .python-version                   # Python runtime baseline
├── .nvmrc                            # Node.js runtime baseline
├── .github/workflows/
│   └── ci.yml                        # Database, backend, frontend and browser checks
├── frontend/
│   ├── README.md
│   ├── .env.example
│   ├── app/                          # Nuxt 4 application source
│   │   ├── pages/                    # Home, Compare, Area Details, API test console
│   │   ├── components/               # Shared presentation components
│   │   ├── utils/                    # Shared API request helpers
│   │   └── assets/css/               # Tailwind and application styling
│   ├── public/                       # Browser assets and verified display map
│   ├── tests/                        # Unit/component and real API browser tests
│   ├── nuxt.config.js                # Build and public API config
│   ├── package.json                  # Scripts and pinned dependencies
│   └── package-lock.json             # Committed npm lockfile
├── backend/
│   ├── README.md
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI setup, CORS and safe errors
│   │   ├── api.py                    # Search, compare, details and health endpoints
│   │   ├── database.py               # Read-only SQLite queries
│   │   ├── models.py                 # Shared JSON response definitions
│   │   └── settings.py               # Environment settings and database path
│   ├── tests/test_api.py             # API journey and failure tests
│   ├── requirements.txt              # Pinned runtime dependencies
│   └── requirements-dev.txt          # Runtime + test dependencies
├── contracts/
│   ├── README.md
│   ├── openapi.json                  # Exported from FastAPI models
│   └── examples/                     # Generated real response examples
├── pipeline/
│   ├── acquire_greater_melbourne.py  # Network acquisition; resumable cache
│   ├── build_greater_melbourne.py    # Offline transformations and SQLite build
│   ├── greater_melbourne_schema.sql  # Executable database schema
│   ├── melbourne_*.py                # Source and spatial helpers
│   ├── document_greater_melbourne.py # Schema/coverage documentation
│   ├── verify_greater_melbourne_rebuild.py
│   ├── test_*.py                     # Calculation, spatial and release tests
│   ├── requirements-*.txt            # Pinned data-processing dependencies
│   └── fixtures/                    # Small regression values; no second database
├── data/
│   └── greater-melbourne-v1/         # One maintained dataset for local/API deployment
│       ├── yfn.sqlite             # The single database used by the backend
│       ├── curated/                  # Generated CSVs; committed
│       ├── audit/                    # Validation evidence; bulky intersections ignored
│       ├── raw/                      # Local downloads; ignored by Git
│       ├── manifest.json             # Data/method/runtime metadata
│       ├── acquisition.json          # Source URLs, timestamps and hashes
│       └── schema-guide.md           # ER diagram and design notes
├── scripts/
│   ├── check_sample.py              # Fast data check usable on a fresh clone
│   └── export_api_contract.py        # OpenAPI and frontend response examples
├── deploy/
│   └── README.md                    # Render UI setup and recovery guide
└── render.yaml                      # Frontend and API deployment definition
```

Keep API dependencies separate from the GIS environment. Keep each application's tests with that application. Shared contract examples belong in `contracts/`; do not maintain different mock shapes in the UI and API. Existing pipeline paths are preserved because the source manifests, tests and rebuild evidence refer to them.

`contracts/` is development and test support: backend tests compare the exported OpenAPI schema with the running app, and frontend comparison tests import its response examples. Keep it with the source. Assessment reports, presentation files, wireframes and document-generation scratch files belong outside this repository in the PGP or a separate working folder. Local dependencies, caches and raw downloads remain ignored by Git; do not include them in a source ZIP.

## Clone and verify the project

### Prerequisites

- Git and access to the team's GitHub repository.
- Python **3.12.14**, matching `.python-version` and the data build. Use a virtual environment for dependencies.
- Node.js **24.20.0** and npm for frontend work, matching `.nvmrc`. The frontend has been built and tested with this version. [Node.js releases](https://nodejs.org/en/about/previous-releases)
- `curl` on `PATH` for data acquisition. Frontend/API contributors do not need the full source downloads.

Runtime pins are repository configuration; they do not install interpreters automatically. Confirm `python --version` and `node --version` in the environment you use. If you use nvm, run `nvm install` and `nvm use` from the repository root.

### Install tools before first checkout

Install Git, Python and Node.js before running the project commands. VS Code is the team's editor; its terminal uses the tools installed on your computer.

| Tool | Purpose and setup |
|---|---|
| Git | Clone and pull the private repository. Obtain repository access from the maintainer. |
| Python 3.12.14 | Runs FastAPI and backend tests. The root `.python-version` records the expected version; it does not install Python. |
| Node.js 24.20.0 and npm | Run Nuxt, install frontend dependencies and generate the static site. Node installations include npm. |
| nvm (optional) | Installs and switches Node versions. It is a separate tool, not an npm package required by the app. |
| VS Code and a browser | Edit code, run two terminals and test the application. |

For macOS/Linux, follow the [official nvm installation instructions](https://github.com/nvm-sh/nvm#installing-and-updating), then reopen your terminal. After cloning, `nvm install` and `nvm use` read the repository's `.nvmrc`. If you install the pinned Node version directly, skip the nvm commands.

Native Windows uses the separate [nvm-windows project](https://github.com/nvm-windows/nvm). Use explicit versions: `nvm install 24.20.0` followed by `nvm use 24.20.0`. The bare nvm commands shown in the macOS/Linux workflow are not the Windows setup instructions. WSL users can follow the Linux workflow within WSL.

Check the tools in a new terminal:

```sh
git --version
node --version
npm --version
python3.12 --version
```

On Windows use `py -3.12 --version` for Python. If using nvm on macOS/Linux, `command -v nvm` should print `nvm`. A “command not found” error means the tool is not installed or loaded in that terminal; reopen the terminal after installation and follow the tool's setup instructions.

No separate SQLite server, Docker, GIS tools or dataset downloads are required to run the frontend and API. The database is included. Pipeline dependencies are only needed by contributors rebuilding data.

### First checkout

Clone the repository, then run the bundled data check:

```sh
git clone https://github.com/wasif-danesh/YFN.git yfn
cd yfn
python3 scripts/check_sample.py
```

On Windows, the equivalent check is `py -3.12 scripts/check_sample.py`.

The check works now using only Python's standard library. It verifies the committed data hashes, CSV/table counts, release metadata, missing values and SQLite integrity. It does not download datasets or re-run spatial processing. A full source rebuild is a separate workflow below.

Read this guide, the relevant [frontend](frontend/README.md) or [backend](backend/README.md) guide and the [API contract](contracts/README.md) before starting a feature. Start with the checked-in real dataset; raw downloads are not needed just to develop a page or endpoint. Assessment requirements and wireframes are maintained separately in the PGP.

### What belongs in Git

Commit application code, dependency manifests/lockfiles, contracts, SQL, documentation, compact curated CSVs, the single SQLite database and small validation reports. Commit database and manifest changes together.

Do not commit `.env`, virtual environments, `node_modules`, build outputs, temporary SQLite journals, raw downloads or bulky generated spatial audits/geometry. `.env.example` is intentionally committed. The current `.gitignore` preserves the local files; it only controls future Git tracking. If files were already tracked in another repository, review its index separately.

Ignored raw snapshots must be retained by the data owner in a team-accessible versioned archive if exact historical reproduction is required. Source APIs may change: reacquiring later is not guaranteed to reproduce today's checksums.

## Local application development

**Use two terminals in VS Code: one for the API and one for the frontend.** Open your cloned project folder in VS Code first; both terminals must start at the repository root (the folder containing this README). The maintainer confirmed this setup works locally. The database and map boundaries are already included; no dataset downloads are needed. See the [backend guide](backend/README.md) for endpoint examples and tests.

### Backend terminal

Run from the repository root. Create the environment and copy `.env` only on first setup:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cp backend/.env.example backend/.env
```

Start the API and leave this terminal running:

```sh
python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv`, activate it with `.venv\Scripts\Activate.ps1`, and copy the file with `Copy-Item backend/.env.example backend/.env`. The subsequent `python` commands are the same. If local policy prevents activation, invoke `.venv\Scripts\python.exe` directly.

The development URLs are API `http://localhost:8000`, OpenAPI UI `http://localhost:8000/docs`, and browser status `http://localhost:8000/api/v1/status`. The API must open `DATABASE_PATH` read-only and resolve relative paths from the repository root. The development example points to the included database.

### Frontend terminal

Open a second terminal from the repository root. Use the Node version in `.nvmrc`. With nvm on macOS/Linux, run:

```sh
nvm install
nvm use
```

First-time setup only (do not overwrite an existing `.env`):

```sh
cp frontend/.env.example frontend/.env
npm --prefix frontend ci
```

Start the frontend and leave this terminal running. Use `--prefix frontend`: the Python backend has no `package.json` and cannot be started with npm:

```sh
npm --prefix frontend run dev
```

Use `Copy-Item` instead of `cp` on PowerShell. The expected frontend URL is `http://localhost:3000`. Commit `package-lock.json` and use `npm ci` for ordinary checkouts; use `npm install` only for intentional dependency changes and commit the resulting lockfile change.

The homepage searches areas and displays a clickable Greater Melbourne map. Compare shows up to three areas with historical rent differences and links to Area Details. Area Details includes an annual population chart, accessible data table and a return link that preserves the comparison. Visit `/api-test-console` for the four API checks and raw JSON. Run `npm --prefix frontend test` for unit/component checks and `npm --prefix frontend run generate` for the static build. See [frontend instructions](frontend/README.md) for real API browser tests.

### Open the app

- [Homepage](http://localhost:3000/)
- [Compare areas](http://localhost:3000/compare)
- [API test console](http://localhost:3000/api-test-console) — expect four successful checks
- [API status](http://localhost:8000/api/v1/status)
- [Interactive API documentation](http://localhost:8000/docs)

Use **localhost** consistently. It is a different browser origin from `127.0.0.1`; the local environment examples already allow `http://localhost:3000`.

### Start again on another day

From the repository root, in terminal 1:

```sh
source .venv/bin/activate
python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

In terminal 2, select the pinned Node version (`nvm use` if using nvm), then run:

```sh
npm --prefix frontend run dev
```

On PowerShell, activate Python with `.venv\Scripts\Activate.ps1`. Press **Ctrl+C** in each terminal to stop its server. Do not recreate environments or recopy `.env` files each day. After pulling dependency changes, rerun the appropriate install command: `python -m pip install -r backend/requirements-dev.txt` or `npm --prefix frontend ci`.

### Configuration

| Variable | Used by | Local example | Render value |
|---|---|---|---|
| `DATABASE_PATH` | API | `data/greater-melbourne-v1/yfn.sqlite` | `data/greater-melbourne-v1/yfn.sqlite` |
| `CORS_ALLOWED_ORIGINS` | API | `["http://localhost:3000"]` | JSON array containing the actual frontend HTTPS origin |
| `NUXT_PUBLIC_API_BASE` | Frontend build | `http://localhost:8000/api/v1` | Optional override; Blueprint derives this from the API’s public URL |
| `PORT` | Render API process | Development command uses 8000 | Supplied by Render; bind to `0.0.0.0` |

The backend implements these settings and parses CORS as a JSON array. An origin includes scheme/host/port but no path or trailing slash. Add approved preview origins explicitly if previews are introduced. Public frontend configuration is visible to visitors and must never contain credentials.

## Database and API contract

Start with the [SQLite database](data/greater-melbourne-v1/yfn.sqlite), [ER diagram](data/greater-melbourne-v1/schema-guide.md), [column dictionary](data/greater-melbourne-v1/data-dictionary.md) and [SQL schema](pipeline/greater_melbourne_schema.sql).

| Tables | Purpose |
|---|---|
| `areas`, `indicators` | Official geographic identities and reusable measure definitions |
| `observations` | One value per area/indicator, with period, method, quality and coverage |
| `population_history` | Annual population and revision status |
| `data_sources`, `source_files` | Dataset provenance and exact downloaded resources |
| `observation_sources`, `observation_components` | Multiple contributing sources, numerators and denominators |
| `methods`, `area_diagnostics` | Calculation definitions, spatial coverage and sensitivity evidence |
| `sample_release` | Metadata for the current database release |

Keep SA2 codes as strings and preserve nulls. Unknown is not zero. The two zero-population SA2s remain in the database but are excluded by its provisional comparison flag. The database supports one boundary edition and one current observation per indicator/area per database release. Future release/history requirements must be reflected consistently in the keys.

The implemented REST endpoints are:

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/areas?query=...&limit=20` | Search eligible areas |
| `GET /api/v1/areas/{sa2_code}` | Area details, indicators and population history |
| `GET /api/v1/compare?sa2=code1,code2` | Compare two or three distinct areas |
| `/api/v1/status` | Browser service/database readiness check; same response as `/health` |
| `GET /health` | Process/database readiness |

See the [implemented contract](contracts/README.md), [OpenAPI](contracts/openapi.json) and real JSON examples. Sources are embedded with indicators and population history; no separate sources endpoint is needed. Keep raw values, units, periods, quality, coverage and provenance available to the client. All comparisons must use the same stored calculations; the UI formats values rather than recalculating indicators.

## Open datasets

| Source | Fields/use | Important limitation |
|---|---|---|
| [ABS Census DataPacks, 2021](https://www.abs.gov.au/census/find-census-data/datapacks) | Victoria SA2 G02 `Median_rent_weekly` | Historical reported rent, not current advertised rent; 358 usable medians |
| [ABS Regional population, 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | SA2 ERP, 2020–2025; growth and denominators | 2025 preliminary; previous estimates may be revised; 359 growth values |
| [ABS ASGS Edition 3 boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files) | 2021 SA2 identity, geometry and `2GMEL` membership | SA2s and suburbs are different geographies |
| [DataVic PTAL Melbourne metro](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro) | `sum_ai_8_9` spatial access index | 360 numeric aggregates, some with very small coverage; no approved ratings |
| [DataVic Open Space](https://discover.data.vic.gov.au/dataset/open-space) | Selected public-open-space polygons divided by ERP | Unmaintained/undated inventory; filter includes sports land and can include water; 354 ratios |

The database records these sources as CC BY 4.0 and retains source-specific limitations and attribution. Project software uses the [MIT licence](LICENSE). Third-party datasets and reference documents retain their respective licences and attribution requirements; the MIT licence does not replace those terms.

See the [data package report](data/greater-melbourne-v1/README.md) and [acquisition manifest](data/greater-melbourne-v1/acquisition.json) for exact resources, hashes and methods. Source validation includes 14 independent QuickStats checks, exact reconciliation of six annual Greater Melbourne population totals, and complete spatial-layer count/ID checks. All four indicator rows are retained for each area even when a value is unavailable.

## Data preparation and refreshes

### Work with the included database

Frontend and backend contributors use the same checked-in `data/greater-melbourne-v1/yfn.sqlite`. The frontend requests JSON from FastAPI; only the backend opens SQLite. Test fixtures may be in memory and must never silently replace unavailable real data.

### Rebuild from original source snapshots

The data contributor uses a separate environment, from the repository root:

```sh
python3.12 -m venv .venv-data
source .venv-data/bin/activate
python -m pip install -r pipeline/requirements-greater-melbourne.txt
```

On Windows, use `py -3.12` to create the environment and `.venv-data\Scripts\Activate.ps1` to activate it. Confirm `curl --version` works.

Most team members only need to clone the repository and run `python scripts/check_sample.py`; the database is already included. Only the data maintainer needs the GIS environment and commands below. For an exact rebuild, restore `data/greater-melbourne-v1/raw/` snapshots matching `acquisition.json`. If snapshots are absent, acquisition downloads the official sources directly:

```sh
python pipeline/acquire_greater_melbourne.py
```

The scripts intentionally stop if a saved source no longer matches its recorded hash. If the live source has changed, the data maintainer must review the source change and deliberately update the snapshot and manifest in the same dataset folder. Preserve old raw snapshots separately if historical reproduction is needed; Git retains prior committed database versions. Do not delete old manifests merely to bypass checksum failures. A fresh download is not guaranteed to reproduce a historical snapshot.

Once matching snapshots are present:

```sh
python pipeline/build_greater_melbourne.py
python pipeline/document_greater_melbourne.py
python -m unittest discover -s pipeline -p 'test_*.py' -v
python pipeline/verify_greater_melbourne_rebuild.py
```

The pipeline uses assertions for validation: do not run it with Python `-O`. Full tests require the raw snapshots; `scripts/check_sample.py` is the separate clean-clone check. Download timestamps and changed source inventories can alter the manifest, so rerun only the offline builder when checking byte-identical reproduction.

The complete Greater Melbourne offline rebuild took approximately 53 seconds in the original environment. That excludes downloads and is not a timing guarantee for other machines.

### Update the single application database

Resolve the production method/coverage decisions, then build and validate the selected real dataset. Review value changes, null counts, geometry repairs, boundary compatibility, provenance and the schema/API contract. The API startup and Render build validate database integrity. Final publication approval remains separate from these technical checks; the current application retains provisional-data notices.

For the initial small SQLite artifact, commit `data/greater-melbourne-v1/yfn.sqlite` and its matching manifest in the same PR. Reviewers should see a human-readable summary of the changes; do not rely on a binary diff alone. Do not hand-edit SQLite, copy it into the frontend's `public/` directory, or run acquisition on every code push. The database path stays the same locally and on Render. Git history preserves prior committed versions; no separate releases folder or database promotion step is needed.

## Team Git workflow

Use `main` as the proposed deployment branch and short-lived feature branches. If the team's repository uses another branch, update CI and Render consistently.

```sh
git switch main
git pull --ff-only origin main
git switch -c feat/area-search

# Make and validate changes, then inspect the diff.
git status
git diff
git add PATHS_YOU_CHANGED
git commit -m "Add area search"
git push -u origin feat/area-search
```

Replace the example branch and staged paths with your work. Open a pull request into `main`, describe the problem and resulting behaviour, list the checks run, and attach UI evidence or a data-change summary when relevant. Obtain a teammate review and resolve required checks before merging. Keep changes focused and avoid committing credentials or unrelated generated files.

Feature-branch pushes should run PR checks once a PR exists; they should not deploy the production services. A merge to the linked `main` branch triggers the appropriate Render build after checks pass, once deployment is configured. API and frontend deployments are independent, so contract changes must tolerate either service updating first.

The repository maintainer should create the shared GitHub repository, add collaborators, push the reviewed initial files, and configure a branch ruleset requiring PR review and the applicable checks. No actual repository URL or team permissions are implied by this guide.

## Deploying to Render

The root [render.yaml](render.yaml) creates a Static Site and a Python Web Service using the **Free API plan selected for this test**. Follow the [step-by-step Render UI guide](deploy/README.md), including the one-time CORS setup and post-deployment checks. Keep Root Directory blank for both services.

The frontend receives the API public URL through the Blueprint. SQLite is checked and packaged with the backend; only `frontend/.output/public` is published as web assets. No pipeline downloads or persistent disk are needed. Normal main-branch auto-deploys wait for GitHub checks, with separate frontend/backend path filters. Initial, manual and Blueprint configuration deployments still require verification.

This configuration supports deployment, but the Free plan is for testing: idle API services sleep and take time to wake. Upgrade the API instance plan before requiring continuous production availability. The provisional dataset still requires publication decisions before the final renter release. [Render Free limitations](https://render.com/docs/free)

## Testing and troubleshooting

| Check | Available now? | Command or implementation requirement |
|---|---|---|
| Committed data consistency | Yes; no downloads | `python scripts/check_sample.py` |
| Full source/calculation tests | Yes; data dependencies and snapshots required | `python -m unittest discover -s pipeline -p 'test_*.py' -v` |
| Reproducible offline build | Yes; matching source snapshots required | `python pipeline/verify_greater_melbourne_rebuild.py` |
| API tests | Yes; backend dev dependencies required | `python -m pytest backend/tests -q` |
| Frontend unit/build checks | Yes | `npm --prefix frontend test` and `npm --prefix frontend run generate` |
| Desktop/mobile API integration | Yes | See [browser test setup](frontend/README.md#tests) |
| Home → Compare → Area Details journey | Yes | Keyboard search, map selection, selection/removal, population history, return navigation, direct reloads and failure states |
| Map identity and integrity | Yes | `python scripts/check_homepage_map.py` |

| Symptom | What to check |
|---|---|
| API cards show loading or a network error | The free API sleeps when idle; the page shows a spinner and explains the wait, so allow up to a minute before retrying. If it persists, inspect API health and CORS |
| `No module named backend` | Run the documented Uvicorn command from the repository root, with the backend virtual environment activated |
| API cannot find the database | Start from repo root; inspect `DATABASE_PATH`; do not set Render Root Directory to `backend/` with a root-level data dependency |
| Browser reports CORS errors | Check the exact frontend origin, JSON parsing of the allowlist and the public API URL |
| UI still calls an old API URL | Rebuild the static site with the corrected public setting |
| Area Details reload returns 404 | Check static fallback generation and rewrite configuration |
| Pipeline reports a hash mismatch | Restore the matching archived snapshot or start a new versioned release; do not bypass the check |
| Full pipeline tests fail after cloning | Raw files are ignored by Git; use the clean-clone check or restore/acquire the source snapshots |
| A push does not deploy | Check linked branch, actual executed CI results, build filters and auto-deploy configuration |

## Project documentation and responsibilities

- [Frontend development and tests](frontend/README.md)
- [Backend development and tests](backend/README.md)
- [Shared API contract](contracts/README.md)
- [Real-data package, ER diagram and verification](data/greater-melbourne-v1/README.md)
- [Render deployment and recovery](deploy/README.md)

The proposal lists Andrew Tran, Sanskrita DSarma, Tin Nguyen and Wasif Danesh. Assign current workstream owners in the team's tracker; this guide does not assign individual responsibilities. Coordinate frontend, API, data and integration/QA work through the shared contract and review process.

Keep this README current when startup commands, dependency pins, source releases, environment settings or deployments change. Keep original assessment documents and wireframes in the separate PGP; a recommendation in an older attachment is not evidence of current team approval.

## Licence

Project source code and project-authored documentation are released under the [MIT License](LICENSE), using GitHub's standard MIT text. Copyright © 2026 Your Friendly Neighbourhood contributors. Third-party data, dependencies and copied reference materials remain subject to their own terms.
