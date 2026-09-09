# Frontend

Nuxt 4, Vue, JavaScript and Tailwind power the temporary **Your Friendly Neighbourhood API test console**. It calls all four endpoints automatically and shows their HTTP status and JSON. Inputs allow different searches and SA2 selections; each request can be retried independently. Errors, nulls and provisional metadata remain visible. The final renter pages and Leaflet map are future work.

## Run locally

Install the Node version in `.nvmrc`. From the repository root, start the [backend](../backend/README.md) in one terminal. In a second terminal:

```sh
cp frontend/.env.example frontend/.env
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open `http://localhost:3000`. On PowerShell, use `Copy-Item` instead of `cp`. The default API is `http://localhost:8000/api/v1`; the backend example allows the localhost frontend origin. Use the same hostname consistently because `localhost` and `127.0.0.1` are distinct browser origins.

## Files

| File | Responsibility |
|---|---|
| `app/pages/index.vue` | Reads Nuxt public API configuration and mounts the console |
| `app/components/ApiConsole.vue` | Inputs, four request cards, status and retry UI |
| `app/utils/api.js` | Endpoint URLs, fetch handling and 90-second timeout |
| `app/assets/css/main.css` | Responsive blue theme and keyboard focus styles |
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

On Windows activate with `.venv\Scripts\Activate.ps1`. Stop any existing server on ports 8000 or 4173 before browser tests: Playwright starts and stops its own API and static preview server. Generate the site with the default local API URL for these tests. The tests exercise all four endpoints, HTTP 422 recovery, page reload and horizontal overflow on desktop and mobile. Screenshots and failure traces are saved under ignored `frontend/test-results/`.

To inspect the generated build manually, run `npm --prefix frontend run preview` and open `http://127.0.0.1:4173`. Add that exact origin to the local backend CORS allowlist and restart the API first. The preview server is for local testing; Render hosts the generated files directly.

CI installs dependencies from the lockfile, runs unit tests, generates the site, checks that no database/backend files are published, and runs browser tests. Extend tests for the final renter journey when those pages are built.

## Deployment configuration

See [Render setup](../deploy/README.md). The Blueprint sets `NUXT_PUBLIC_API_ORIGIN` from the API service's public Render URL; Nuxt appends `/api/v1`. Optional `NUXT_PUBLIC_API_BASE` overrides that with a complete URL. Changing either requires a static-site rebuild. Never put secrets, SQLite or raw datasets in `public/` or public Nuxt configuration.

## Browser service check

The frontend uses `/api/v1/status` for its Service health card. `/health` remains available for Render’s configured health check. Both routes run the same database readiness handler and return the same JSON and error responses. This change avoids the observed browser-profile block on `/health`; it cannot guarantee compatibility with every extension. Deploy the backend with the new route before deploying the frontend, then retry in the affected regular browser profile.
