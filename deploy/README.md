# Deploy the API test console to Render

The root [render.yaml](../render.yaml) is the single deployment definition. It creates `yfn-api` (Python Web Service, Free plan, Singapore region) and `yfn-web` (Static Site). Both build from the repository root. The user selected Free for this test; no service has been provisioned by writing the file.

The Free API sleeps after 15 minutes without traffic and can take about a minute to wake. The console allows 90 seconds per request and offers retries. Free is suitable for this test; choose an appropriate paid instance before requiring production availability. Usage allowances still apply. [Render Free documentation](https://render.com/docs/free)

## Before opening Render

1. Run the checks in the root README and frontend guide locally. Review and commit the application, lockfiles, documentation, root `render.yaml`, database and its matching manifest.
2. Push the reviewed commit to your GitHub `main` branch. This guide does not push for you.
3. In GitHub → Actions, confirm all three jobs pass: database integrity, backend API tests, and frontend tests/build. Allow GitHub Actions if the repository has disabled it.
4. Ensure Render's GitHub integration can access your private repository. A private repository does not make the deployed website private.

## Create both services in Render

1. Open your Render Dashboard. Choose **New → Blueprint**.
2. Connect/select the GitHub repository. Name the Blueprint `yfn`, choose branch `main`, and use Blueprint Path `render.yaml`.
3. Review the proposed services. Confirm the API plan is **Free**, region is **Singapore**, and the frontend is a **Static Site**. Leave **Root Directory blank** for both services.
4. When prompted for `CORS_ALLOWED_ORIGINS`, enter `[]` for the initial creation. This lets the API start while its frontend URL is still unknown; browser calls will fail until the next section is complete.
5. Click **Deploy Blueprint**. Inspect both build/deploy logs and wait for the services to become live. If Render reports a Blueprint validation error, resolve it before applying changes.

The dashboard flow and Blueprint review are documented by [Render](https://render.com/docs/infrastructure-as-code). Use this Blueprint once; creating another would provision duplicate services.

## Connect browser access — required once

1. Open `yfn-web` and copy its actual public HTTPS URL. Names can acquire suffixes; do not assume the hostname.
2. Open `yfn-api` → **Environment**. Set `CORS_ALLOWED_ORIGINS` to a JSON array containing that origin, for example:

   ```json
   ["https://your-actual-frontend.onrender.com"]
   ```

3. Use the origin only: no path or trailing slash. Choose **Save and deploy** and wait for the API deployment to finish.
4. The frontend's `NUXT_PUBLIC_API_ORIGIN` automatically references the API's public `RENDER_EXTERNAL_URL`. Check it under `yfn-web` → Environment if requests target an unexpected host. Do not use Render's private network hostname.
5. If you change the frontend API setting later, select **Save, rebuild, and deploy** for the static site; the URL is embedded during generation. For a custom API URL, set `NUXT_PUBLIC_API_BASE` to its full HTTPS URL ending in `/api/v1`.

The CORS setting uses `sync: false`, so the value you enter is retained outside the Blueprint. Environment controls are described in [Render's environment guide](https://render.com/docs/configure-environment-variables). CORS is not authentication.

## Verify your deployment

- Open the API's `/health`. It should return HTTP 200 with `"status": "ok"` and `"database": "ready"`.
- Open the frontend. Allow the API to wake, then expect **4 of 4 requests successful** with JSON in every card.
- Search for `carl`, change the detail SA2 code, and try comparison with only one code. Expect an HTTP 422 error; restore `206041117,213031348` and retry successfully.
- Reload the homepage, check it on a phone, and confirm the API base shown is the public HTTPS API address. If JSON fails, inspect API logs, the exact CORS origin and the browser Network panel.
- Confirm source dates, nulls and `publication_ready: false` remain visible. This is an explicitly labelled development console, not the final renter-facing data release.
- Record the Git commit and both live URLs in the team tracker. Health means the app/database are operational, not that provisional methods have been approved.

## Subsequent changes and recovery

Open a feature branch, make changes, run checks, then submit a PR. Merge reviewed changes to `main`. Both services use **After CI Checks Pass**, with path filters so frontend changes rebuild the site and backend/data changes rebuild the API. Shared contract and CI changes affect both. Keep API changes backward compatible because the services deploy independently.

Initial deployment, manual deployment and Blueprint configuration syncs require their own verification; do not assume normal auto-deploy gating protects those paths. Blueprint auto-sync can apply configuration changes directly, so review `render.yaml` changes carefully. See [deployment behaviour](https://render.com/docs/deploys) and [Blueprint settings](https://render.com/docs/infrastructure-as-code).

The backend build validates the checked-in database; it does not download or rebuild source datasets. Runtime SQLite is read-only. No persistent disk is needed because every deployment includes the maintained database from Git. Only `frontend/.output/public` is published by the Static Site.

If a deployment fails, inspect its build log and GitHub checks. For a live regression, roll back to a verified deployment or revert the code/database commit together, then recheck both services. Review environment variables separately: code rollback does not restore changed environment settings. Keep the root Blueprint in sync with deliberate service-setting changes.

## Local verification evidence

Verified on 9 September 2026 with Python 3.12.14 and Node 24.20.0: 36 backend tests, 8 frontend unit/component tests and 2 Chromium browser tests (desktop and mobile) passed. A clean `npm ci` and static production build passed; the build check found no database or backend files in published assets. Database hashes/integrity passed for all 361 SA2s. The Blueprint passed Render’s published JSON schema validation. Desktop/mobile screenshots were visually reviewed. These are local checks; Render deployment and its generated URLs still require the dashboard verification above.

## Browser service check

The frontend uses `/api/v1/status` for its Service health card. `/health` remains available for Render’s configured health check. Both routes run the same database readiness handler and return the same JSON and error responses. This change avoids the observed browser-profile block on `/health`; it cannot guarantee compatibility with every extension. Deploy the backend with the new route before deploying the frontend, then retry in the affected regular browser profile.
