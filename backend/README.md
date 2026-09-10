# Backend — Your Friendly Neighbourhood

FastAPI reads the single [SQLite database](../data/greater-melbourne-v1/yfn.sqlite) and returns JSON. No dataset downloads, GIS packages or separate database server are needed.

## Start locally

For the complete API and frontend workflow, follow [Local application development](../README.md#local-application-development). Run from the repository root with Python 3.12:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cp backend/.env.example backend/.env
python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

Create the environment and copy the example only on initial setup; do not overwrite an existing `.env`. Subsequently activate the environment and start Uvicorn. Reinstall dependencies when requirements change.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
Copy-Item backend/.env.example backend/.env
python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

Open [interactive documentation](http://localhost:8000/docs) and use **Try it out**. Check [health](http://localhost:8000/health) first. Stop the server with Ctrl+C.

## Where to work

| File | Responsibility |
|---|---|
| `app/main.py` | Creates FastAPI, registers routes, CORS and safe errors |
| `app/api.py` | Four endpoint functions and input validation |
| `app/database.py` | Read-only SQLite connections, SQL queries and response composition |
| `app/models.py` | JSON response definitions shared by Compare and Details |
| `app/settings.py` | Environment configuration and database path |
| `tests/test_api.py` | Journey, data, failure, settings and CORS tests |

Request flow: **frontend → api.py → database.py → yfn.sqlite → JSON**. Synchronous endpoints run SQLite work in FastAPI's worker thread pool. No ORM or extra controller/service/repository layers are needed.

## Endpoints

| GET path | Behaviour |
|---|---|
| `/api/v1/status` | Browser service/database readiness check; same response as `/health` |
| `/health` | 200 when the database is readable and compatible; otherwise 503 |
| `/api/v1/areas?query=carl&limit=20` | Case-insensitive official SA2-name search; comparable areas only |
| `/api/v1/compare?sa2=206041117,213031348` | Four indicators for two or three distinct comparable codes, in supplied order |
| `/api/v1/areas/206041117` | Carlton identity, four indicators, annual population counts and sources |

Empty/whitespace search lists names alphabetically. Exact matches rank first, then prefixes, then other partial matches. Query length is at most 100 characters; limit is 1–50. Suburb aliases are not implemented. Use the string SA2 codes from search in subsequent requests.

Compare accepts one comma-separated `sa2` parameter without spaces. A single selected area is a frontend state: fetch Details while prompting for another area. Details can describe an ineligible area, but Compare rejects it. The frontend preserves selection in the URL when navigating back from Details.

The homepage map uses a separate verified display-only GeoJSON asset with the same SA2 codes. It is rendered by the frontend with Leaflet; no map API endpoint is needed. See the frontend guide for rebuilding the asset.

## JSON and data meaning

See the [contract guide](../contracts/README.md), [OpenAPI export](../contracts/openapi.json) and [example responses](../contracts/examples/).

- Numbers remain numeric and missing values remain JSON `null`.
- Indicators include units, dates, method IDs/status, quality notes, source URLs and roles. Internal source file paths and workbook cells are not exposed.
- `population_history` contains annual counts, not annual growth percentages. Years/revision status are explicit; `population_sources` contains their sources.
- `meta.publication_ready` is currently false. Health reports technical readiness, not approval to publish. No ratings are invented for provisional transport measures.
- The API never writes SQLite, downloads datasets, calculates new indicators or falls back to dummy data. Connections close after each response and read one transaction snapshot.

Errors have one shape:

```json
{"error":{"code":"AREA_NOT_FOUND","message":"That area was not found."}}
```

422 means invalid input/ineligible selection; 404 unknown area; 503 unavailable/incompatible database. The UI should offer retry for 503.

## Configuration

`DATABASE_PATH` defaults to `data/greater-melbourne-v1/yfn.sqlite`. Relative paths resolve from the repository root even if the working directory changes. `CORS_ALLOWED_ORIGINS` is a JSON array of HTTP(S) origins, e.g. `["http://localhost:3000"]`; no trailing slash/path. Set the actual frontend HTTPS origin on Render. CORS is browser access policy, not authentication.

Uvicorn's `--env-file backend/.env` explicitly loads local settings; importing the app alone does not load `.env`. Render supplies environment variables directly. If using `http://127.0.0.1:3000`, add that exact origin too.

## Tests and API changes

```sh
python -m pytest backend/tests -q
python scripts/check_sample.py
python -m scripts.export_api_contract
```

Tests need no running server, raw downloads or GIS dependencies. They cover search, bounds, comparison ordering, consistent indicators, all 361 Details responses, nulls, annual counts, missing/corrupt databases, read-only access, configuration, CORS and OpenAPI drift. Mutation tests use disposable copies; the shared database hash is checked for accidental changes.

When changing response fields, update models, implementation and tests together, regenerate the contract, then rerun tests. Commit examples alongside code for the frontend team. GitHub CI runs backend tests and database checks. Two upstream test-library deprecation warnings may appear with the pinned versions; they do not affect test results.

The frontend now includes unit/component tests and desktop/mobile browser tests against the real API. See [frontend tests](../frontend/README.md#tests). The final renter journey will need additional tests as it is implemented.

## Render

The root [Render Blueprint](../render.yaml) installs runtime dependencies, validates the committed database and starts Uvicorn on Render’s port. Both services use repository-root build context. See the [Render UI guide](../deploy/README.md) for the Free-plan test deployment, CORS setup and verification. No external service has been deployed by creating these files.
