# Your Friendly Neighbourhood

**A Greater Melbourne area-comparison website for renters finding their feet in a new city.**

Your Friendly Neighbourhood brings together housing, public transport, population and public open-space information so renters can compare areas and understand the trade-offs. It is designed for people unfamiliar with Melbourne, including new immigrants, international students and interstate migrants.

The planned journey is **Home → Compare → Area Details**. Users can compare two or three Statistical Areas Level 2 (SA2s), inspect the underlying measures and see their source dates and limitations. SA2s do not necessarily match suburb boundaries. The project supports the themes of Sustainable Development Goal 11; its measures are not official UN indicators.

## Project status

| Component | Current state |
|---|---|
| Requirements and wireframes | Available in [project documentation](docs/requirements.md) and [references](docs/references/README.md) |
| Real development data | Prepared for all **361 Greater Melbourne SA2s**, using 2021 boundaries |
| SQLite, schema and ER diagram | Built and verified; **1,444 indicator rows** and **2,166 population-history rows** |
| Data pipeline | Acquisition, offline processing and validation scripts implemented |
| Frontend and REST API | Workspace folders and environment examples prepared; application code has not been implemented |
| GitHub checks | Initial workflow validates the committed data sample; application checks are still to be added |
| Render | Reference configuration prepared; no active Blueprint or deployed service is established by this repository |

The real dataset is suitable for development and schema design. Transport aggregation, coverage eligibility and the open-space filter remain provisional. `publication_ready=false` is preserved. Application development can proceed while the team resolves these definitions.

At preparation on 8 September 2026, this local workspace had not yet been initialized as a Git repository and no GitHub repository URL or deployed service URLs had been assigned. Replace the clone placeholder below when the maintainer creates the shared repository; update this status table when the application and deployments are in place.

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

The initial scope does not include accounts, maps, property listings, ML forecasts, Redis or an overall best-neighbourhood score.

## Repository structure

The top-level workspaces below are present. Files marked **planned** will be created when the applications are implemented; this tree is not a claim that those entry points already run.

```text
yfn/
├── README.md                         # Team onboarding and operating guide
├── LICENSE                           # MIT licence for project software
├── AGENTS.md                         # Instructions for coding assistants
├── .editorconfig                     # Shared text conventions
├── .gitignore                        # Environments, secrets and bulky outputs
├── .gitattributes                    # Stable line endings for checksummed files
├── .python-version                   # Python runtime baseline
├── .nvmrc                            # Node.js runtime baseline
├── .github/workflows/
│   └── ci.yml                        # Committed-data checks; extend for the app
├── frontend/
│   ├── README.md
│   ├── .env.example
│   ├── app/                          # Planned Nuxt 4 application source
│   │   ├── pages/                    # Home, Compare, Area Details
│   │   ├── components/               # Shared presentation components
│   │   ├── composables/              # Shared API client and state helpers
│   │   └── assets/css/               # Tailwind and application styling
│   ├── public/                       # Planned browser-public assets only
│   ├── tests/                        # Planned component/UI tests
│   ├── nuxt.config.js                # Planned build and public API config
│   ├── package.json                  # Planned scripts and dependencies
│   └── package-lock.json             # Planned committed npm lockfile
├── backend/
│   ├── README.md
│   ├── .env.example
│   ├── app/                          # Planned Python package
│   │   ├── main.py                   # FastAPI ASGI entry point
│   │   ├── api/                      # Request handlers and route definitions
│   │   ├── schemas/                  # Request/response models
│   │   ├── repositories/             # Parameterized read-only database queries
│   │   ├── services/                 # Response composition and application logic
│   │   └── core/                     # Configuration and shared dependencies
│   ├── tests/                        # Planned API and repository tests
│   ├── requirements.txt              # Planned pinned runtime dependencies
│   └── requirements-dev.txt          # Planned runtime + test dependencies
├── contracts/
│   ├── README.md
│   ├── openapi.json                  # Planned export from FastAPI models
│   └── examples/                     # Planned reviewed JSON response examples
├── pipeline/
│   ├── acquire_greater_melbourne.py  # Network acquisition; resumable cache
│   ├── build_greater_melbourne.py    # Offline transformations and SQLite build
│   ├── greater_melbourne_schema.sql  # Executable sample schema
│   ├── melbourne_*.py                # Source and spatial helpers
│   ├── document_greater_melbourne.py # Schema/coverage documentation
│   ├── verify_greater_melbourne_rebuild.py
│   ├── test_*.py                     # Calculation, spatial and release tests
│   ├── requirements-*.txt            # Pinned data-processing dependencies
│   └── *_real_sample.py             # Original sample scripts/shared helpers
├── data/
│   ├── samples/
│   │   ├── real-sa2-v1/              # Original four-area evidence, preserved
│   │   └── greater-melbourne-v1/
│   │       ├── curated/              # Compact normalized CSVs; committed
│   │       ├── audit/                # Reports committed; large intersections ignored
│   │       ├── raw/                  # Local original downloads; ignored
│   │       ├── sample.sqlite         # Real development database; committed
│   │       ├── manifest.json         # Release/method/runtime metadata
│   │       ├── acquisition.json      # Source URLs, timestamps and hashes
│   │       └── schema-guide.md       # ER diagram and design notes
│   └── releases/
│       ├── README.md
│       ├── active.sqlite            # Planned approved runtime artifact
│       └── manifest.json            # Planned matching release manifest
├── scripts/
│   └── check_sample.py              # Fast check usable on a fresh clone
├── deploy/
│   └── render.yaml.example          # Reference only; activate after app checks exist
├── docs/                            # Requirements, decisions and original references
└── render.yaml                      # Planned active Render Blueprint
```

Keep API dependencies separate from the GIS environment. Keep each application's tests with that application. Shared contract examples belong in `contracts/`; do not maintain different mock shapes in the UI and API. Existing pipeline paths are preserved because the source manifests, tests and rebuild evidence refer to them.

## Clone and verify the project

### Prerequisites

- Git and access to the team's GitHub repository.
- Python **3.12.14**, matching `.python-version` and the data build. Use a virtual environment for dependencies.
- Node.js **24.20.0** and npm for frontend work, matching `.nvmrc`. Node 24 is an LTS release; the application must still validate its package compatibility when scaffolded. [Node.js releases](https://nodejs.org/en/about/previous-releases)
- `curl` on `PATH` for data acquisition. Frontend/API contributors do not need the full source downloads.

Runtime pins are repository configuration; they do not install interpreters automatically. Confirm `python --version` and `node --version` in the environment you use. If you use nvm, run `nvm install` and `nvm use` from the repository root.

### First checkout

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual HTTPS or SSH clone URL supplied by the maintainer:

```sh
git clone YOUR_GITHUB_REPOSITORY_URL yfn
cd yfn
python3 scripts/check_sample.py
```

On Windows, the equivalent check is `py -3.12 scripts/check_sample.py`.

The check works now using only Python's standard library. It verifies the committed sample hashes, CSV/table counts, release metadata, missing values and SQLite integrity. It does not download datasets or re-run spatial processing. A full source rebuild is a separate workflow below.

Read [requirements](docs/requirements.md), [project decisions](docs/project-context.md) and the [API/data proposal](docs/data-and-api.md) before starting a feature. Start with the checked-in real sample; do not spend time reproducing raw downloads just to develop a page or endpoint.

### What belongs in Git

Commit application code, dependency manifests/lockfiles, contracts, SQL, documentation, compact curated CSVs, sample databases and small validation reports. Commit an approved runtime SQLite file and its manifest together when release preparation is implemented.

Do not commit `.env`, virtual environments, `node_modules`, build outputs, temporary SQLite journals, raw downloads or bulky generated spatial audits/geometry. `.env.example` is intentionally committed. The current `.gitignore` preserves the local files; it only controls future Git tracking. If files were already tracked in another repository, review its index separately.

Ignored raw snapshots must be retained by the data owner in a team-accessible versioned archive if exact historical reproduction is required. Source APIs may change: reacquiring later is not guaranteed to reproduce today's checksums.

## Local application development

**The following startup commands are implementation targets. They become runnable once the API and Nuxt entry points, dependency files and scripts have been added.** The workspace READMEs describe their expected responsibilities. Do not install guessed dependencies or assume a web application exists at this stage.

### Backend terminal

Run from the repository root after the backend is implemented:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cp backend/.env.example backend/.env
python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv`, activate it with `.venv\Scripts\Activate.ps1`, and copy the file with `Copy-Item backend/.env.example backend/.env`. The subsequent `python` commands are the same. If local policy prevents activation, invoke `.venv\Scripts\python.exe` directly.

The intended development URLs are API `http://localhost:8000`, OpenAPI UI `http://localhost:8000/docs`, and health `http://localhost:8000/health`. The API must open `DATABASE_PATH` read-only and resolve relative paths from the repository root. The development example points to the existing sample database.

### Frontend terminal

In a second terminal, from the repository root after frontend scaffolding:

```sh
cp frontend/.env.example frontend/.env
npm --prefix frontend ci
npm --prefix frontend run dev
```

Use `Copy-Item` instead of `cp` on PowerShell. The expected frontend URL is `http://localhost:3000`. Commit `package-lock.json` and use `npm ci` for ordinary checkouts; use `npm install` only for intentional dependency changes and commit the resulting lockfile change.

The scaffold must define `dev`, `generate`, `lint` and `test` npm scripts, declare `runtimeConfig.public.apiBase`, and implement the planned static routes. For static generation, the intended output is `frontend/.output/public`. [Nuxt deployment guidance](https://nuxt.com/docs/3.x/getting-started/deployment)

### Configuration

| Variable | Used by | Local example | Render value |
|---|---|---|---|
| `DATABASE_PATH` | API | `data/samples/greater-melbourne-v1/sample.sqlite` | `data/releases/active.sqlite`, once approved |
| `CORS_ALLOWED_ORIGINS` | API | `["http://localhost:3000"]` | JSON array containing the actual frontend HTTPS origin |
| `NUXT_PUBLIC_API_BASE` | Frontend build | `http://localhost:8000/api/v1` | Actual public API HTTPS URL ending in `/api/v1` |
| `PORT` | Render API process | Development command uses 8000 | Supplied by Render; bind to `0.0.0.0` |

These names are the proposed settings contract for implementation. CORS must parse the documented JSON array. An origin includes scheme/host/port but no path or trailing slash. Add approved preview origins explicitly if previews are introduced. Public frontend configuration is visible to visitors and must never contain credentials.

## Database and API contract

Start with the [SQLite sample](data/samples/greater-melbourne-v1/sample.sqlite), [ER diagram](data/samples/greater-melbourne-v1/schema-guide.md), [column dictionary](data/samples/greater-melbourne-v1/data-dictionary.md) and [SQL schema](pipeline/greater_melbourne_schema.sql).

| Tables | Purpose |
|---|---|
| `areas`, `indicators` | Official geographic identities and reusable measure definitions |
| `observations` | One value per area/indicator, with period, method, quality and coverage |
| `population_history` | Annual population and revision status |
| `data_sources`, `source_files` | Dataset provenance and exact downloaded resources |
| `observation_sources`, `observation_components` | Multiple contributing sources, numerators and denominators |
| `methods`, `area_diagnostics` | Calculation definitions, spatial coverage and sensitivity evidence |
| `sample_release` | Metadata for the current sample database file |

Keep SA2 codes as strings and preserve nulls. Unknown is not zero. The two zero-population SA2s remain in the sample but are excluded by its provisional comparison flag. The sample supports one boundary edition and one current observation per indicator/area per database release. Future release/history requirements must be reflected consistently in the keys.

The intended REST endpoints are:

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/areas?query=...&limit=20` | Search eligible areas |
| `GET /api/v1/areas/{sa2_code}` | Area details, indicators and population history |
| `GET /api/v1/compare?sa2=code1,code2` | Compare two or three distinct areas |
| `GET /api/v1/sources` | Source metadata and limitations |
| `GET /health` | Process/database readiness |

These endpoints are proposed, not implemented. Establish FastAPI response models first, export the contract into `contracts/`, and use it for both API and UI tests. Keep raw values, units, periods, quality, coverage and provenance available to the client. All comparisons must use the same stored calculations; the UI formats values rather than recalculating indicators.

## Open datasets

| Source | Fields/use | Important limitation |
|---|---|---|
| [ABS Census DataPacks, 2021](https://www.abs.gov.au/census/find-census-data/datapacks) | Victoria SA2 G02 `Median_rent_weekly` | Historical reported rent, not current advertised rent; 358 usable medians |
| [ABS Regional population, 2024–25](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | SA2 ERP, 2020–2025; growth and denominators | 2025 preliminary; previous estimates may be revised; 359 growth values |
| [ABS ASGS Edition 3 boundaries](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files) | 2021 SA2 identity, geometry and `2GMEL` membership | SA2s and suburbs are different geographies |
| [DataVic PTAL Melbourne metro](https://discover.data.vic.gov.au/en_AU/dataset/public-transport-accessibility-level-ptal-melbourne-metro) | `sum_ai_8_9` spatial access index | 360 numeric aggregates, some with very small coverage; no approved ratings |
| [DataVic Open Space](https://discover.data.vic.gov.au/dataset/open-space) | Selected public-open-space polygons divided by ERP | Unmaintained/undated inventory; filter includes sports land and can include water; 354 ratios |

The sample records these sources as CC BY 4.0 and retains source-specific limitations and attribution. Project software uses the [MIT licence](LICENSE). Third-party datasets and reference documents retain their respective licences and attribution requirements; the MIT licence does not replace those terms.

See the [sample report](data/samples/greater-melbourne-v1/README.md) and [acquisition manifest](data/samples/greater-melbourne-v1/acquisition.json) for exact resources, hashes and methods. Source validation includes 14 independent QuickStats checks, exact reconciliation of six annual Greater Melbourne population totals, and complete spatial-layer count/ID checks. All four indicator rows are retained for each area even when a value is unavailable.

## Data preparation and refreshes

### Work with the existing sample

Frontend and backend contributors can use the checked-in database immediately. Keep synthetic fixtures separate from real samples, but use the same eventual database loader and API shape. Synthetic values must be labelled and must never silently replace unavailable real data.

### Rebuild from original source snapshots

The data contributor uses a separate environment, from the repository root:

```sh
python3.12 -m venv .venv-data
source .venv-data/bin/activate
python -m pip install -r pipeline/requirements-greater-melbourne.txt
```

On Windows, use `py -3.12` to create the environment and `.venv-data\Scripts\Activate.ps1` to activate it. Confirm `curl --version` works.

For exact reproduction, restore the archived `raw/` folders matching the committed acquisition manifests. After restoring them, run the offline builder and tests below. On a completely fresh clone without archived snapshots, the current acquisition scripts depend on the original four-area raw files; acquire those first:

```sh
python pipeline/acquire_real_sample.py
python pipeline/acquire_greater_melbourne.py
```

The scripts intentionally stop if a saved source no longer matches its recorded hash. If the live source has changed, treat that as a new data release: preserve the existing evidence and adapt acquisition to a new versioned output folder. Do not delete old manifests merely to bypass checksum failures. A fresh download is not guaranteed to reproduce a historical snapshot.

Once matching snapshots are present:

```sh
python pipeline/build_greater_melbourne.py
python pipeline/document_greater_melbourne.py
python -m unittest discover -s pipeline -p 'test_*.py' -v
python pipeline/verify_greater_melbourne_rebuild.py
```

The pipeline uses assertions for validation: do not run it with Python `-O`. Full tests require the raw snapshots; `scripts/check_sample.py` is the separate clean-clone check. Download timestamps and changed source inventories can alter the manifest, so rerun only the offline builder when checking byte-identical reproduction.

The complete Greater Melbourne sample's measured offline rebuild took approximately 53 seconds in the original environment. That excludes downloads and is not a timing guarantee for other machines.

### Prepare an application data release

Resolve the production method/coverage decisions, then build and validate the selected real dataset. Review value changes, null counts, geometry repairs, boundary compatibility, provenance and the schema/API contract. The API implementation must add a release-validation check before deployment is enabled.

For the initial small SQLite artifact, commit `data/releases/active.sqlite` and its matching manifest in the same PR. Reviewers should see a human-readable summary of the changes; do not rely on a binary diff alone. Do not hand-edit SQLite, copy it into the frontend's `public/` directory, or run acquisition on every code push. See [release conventions](data/releases/README.md).

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

### Intended deployment policy

Configure **After CI Checks Pass**, represented by `autoDeployTrigger: checksPass`, for both services. Render supports separate services and path filters for one repository. Keep **Root Directory blank** for both services so commands run from the repository root and the API can access `data/releases/`. Files outside a configured subdirectory root are otherwise unavailable. [Render monorepo support](https://render.com/docs/monorepo-support)

| Change | Expected automatic deployment |
|---|---|
| `frontend/**` | Static site |
| `backend/**` or `data/releases/**` | API |
| `contracts/**` or `.github/workflows/**` | Both |
| `pipeline/**`, sample data or ordinary documentation only | Neither; promote a validated runtime artifact separately |
| Active `render.yaml` | Blueprint configuration is processed; service changes may trigger deployment |

The filters are in [the reference Blueprint](deploy/render.yaml.example). It is deliberately inactive because the application entry points, application CI checks and approved release artifact do not exist yet. Do not copy it to `render.yaml` until the following activation steps are complete.

### First deployment: maintainer steps

1. Implement the API and frontend, commit their dependency files/lockfile, and confirm the local commands above work.
2. Add mandatory API tests, frontend lint/tests/static build, contract checks and runtime-release validation to CI. Run checks on PRs **and pushes to `main`**. The current data-only check does not establish application deployability.
3. Prepare the approved runtime database/manifest, implement startup validation and `/health`, and verify that no database or raw source files appear in the generated frontend directory.
4. Copy `deploy/render.yaml.example` to root `render.yaml`. Review service names, branch, API region and instance plan. Add the chosen plan/region explicitly before creating services; no hosting budget is assumed. Validate the Blueprint in Render before applying it. [Blueprint reference](https://render.com/docs/blueprint-spec)
5. Connect the team's GitHub repository to the Render workspace. Create the API first, or use the reviewed Blueprint to create both services. With a Blueprint, `sync: false` settings are entered during setup. If creating both together, update/rebuild the static site after the actual public API URL is known.
6. Configure the settings below. Use the actual service URLs returned by Render; the proposed names do not guarantee specific available hostnames.
7. Deploy and verify `/health`, one area response, Home → Compare → Area Details, missing-data states, CORS and direct-link reloads. Confirm the deployed commit and database release match the reviewed version.
8. Enable automatic deployment after CI checks pass, merge a small reviewed change, and verify that only the expected service rebuilds. Update this README with the real repository and service URLs.

The first deployment, manual deployments and configuration changes need explicit verification; a future automatic-deployment policy is not proof that they have already passed CI. Render treats `neutral` and `skipped` GitHub checks as passing and does not deploy when it detects no checks. Required application checks must therefore really execute and fail on missing prerequisites. [Render deployment behaviour](https://render.com/docs/deploys)

### Service settings after implementation

| Setting | API Web Service | Frontend Static Site |
|---|---|---|
| Linked branch | `main` | `main` |
| Root Directory | Blank: repository root | Blank: repository root |
| Runtime | Python; `.python-version` | Node for build; `NODE_VERSION=24.20.0` |
| Build command | `python -m pip install -r backend/requirements.txt` | `npm --prefix frontend ci && npm --prefix frontend run generate` |
| Start command | `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` | None |
| Publish directory | Not applicable | `frontend/.output/public` |
| Health check | `/health` | Verify generated pages and assets |
| Data | Checked-in approved SQLite artifact | JSON requested from the API |

The API launch pattern follows [Render's FastAPI guidance](https://render.com/docs/deploy-fastapi). Render can read the Python version from the repository's [`.python-version` file](https://render.com/docs/python-version). A persistent database disk is unnecessary for this read-only artifact design.

Set `NUXT_PUBLIC_API_BASE` to the public API HTTPS URL plus `/api/v1`; the renter's browser cannot use an internal Render hostname. Set `CORS_ALLOWED_ORIGINS` to a JSON array containing the static site's actual origin. Rebuild the static site after changing its API URL, because static configuration is embedded at build time.

The example rewrite sends unmatched frontend paths to `/200.html`. The Nuxt build must produce that fallback and handle direct Area Details links. Verify `/200.html`, unknown-area behaviour and a direct reload of an area URL before release; adjust prerendering/routing if the scaffold uses a different strategy. [Render rewrite rules](https://render.com/docs/redirects-rewrites)

### Subsequent deployments and recovery

Merge reviewed work into `main`, let CI complete, and inspect the affected Render service's build/deploy logs. A new database is delivered through the same commit-based artifact process as API code. Keep a record of the Git commit, data release ID and verification outcome.

If a release fails, inspect the failing check or build log first. For a live regression, restore a previously verified code/database combination using Render's deployment controls or a reviewed Git revert. Verify the API, data release and UI together; environment changes must also be reviewed because they are not automatically reverted with code. If deploying a specific commit, check the resulting auto-deploy setting before resuming normal releases. [Render manual deployments](https://render.com/docs/deploys#manual-deploys)

## Testing and troubleshooting

| Check | Available now? | Command or implementation requirement |
|---|---|---|
| Committed sample consistency | Yes; no downloads | `python scripts/check_sample.py` |
| Full source/calculation tests | Yes; data dependencies and snapshots required | `python -m unittest discover -s pipeline -p 'test_*.py' -v` |
| Reproducible offline build | Yes; matching source snapshots required | `python pipeline/verify_greater_melbourne_rebuild.py` |
| API tests | Planned | `python -m pytest backend/tests` once its dev requirements/tests exist |
| Frontend checks | Planned | `npm --prefix frontend run lint`, `npm --prefix frontend test`, `npm --prefix frontend run generate` |
| User journey/accessibility | Planned | Test search/compare/details, keyboard use, direct links, loading/errors and missing values |

| Symptom | What to check |
|---|---|
| `package.json` or `backend.app.main` is missing | Those application files have not been implemented yet; the workspace folders alone are not runnable apps |
| API cannot find the database | Start from repo root; inspect `DATABASE_PATH`; do not set Render Root Directory to `backend/` with a root-level data dependency |
| Browser reports CORS errors | Check the exact frontend origin, JSON parsing of the allowlist and the public API URL |
| UI still calls an old API URL | Rebuild the static site with the corrected public setting |
| Area Details reload returns 404 | Check static fallback generation and rewrite configuration |
| Pipeline reports a hash mismatch | Restore the matching archived snapshot or start a new versioned release; do not bypass the check |
| Full pipeline tests fail after cloning | Raw files are ignored by Git; use the clean-clone check or restore/acquire the source snapshots |
| A push does not deploy | Check linked branch, actual executed CI results, build filters and auto-deploy configuration |

## Project documentation and responsibilities

- [Project context and decisions](docs/project-context.md)
- [Requirements and page corrections](docs/requirements.md)
- [Data preparation and API proposal](docs/data-and-api.md)
- [Real-data package, ER diagram and verification](data/samples/greater-melbourne-v1/README.md)
- [Original reference documents and wireframes](docs/references/README.md)
- [Coding-assistant guidance](AGENTS.md)

The proposal lists Andrew Tran, Sanskrita DSarma, Tin Nguyen and Wasif Danesh. Assign current workstream owners in the team's tracker; this guide does not assign individual responsibilities. Coordinate frontend, API, data and integration/QA work through the shared contract and review process.

Keep this README current when startup commands, dependency pins, source releases, environment settings or deployments change. Preserve original reference documents and record decisions separately; a recommendation in an older attachment is not evidence of current team approval.

## Licence

Project source code and project-authored documentation are released under the [MIT License](LICENSE), using GitHub's standard MIT text. Copyright © 2026 Your Friendly Neighbourhood contributors. Third-party data, dependencies and copied reference materials remain subject to their own terms.
