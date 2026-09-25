# Shared API contract

The implemented contract is defined by [response models](../backend/app/models.py) and exported to [openapi.json](openapi.json). Earlier proposals are design history where they differ from this implementation.

The frontend can use these real, labelled responses:

- [Search](examples/search.json): `areas`, `meta`.
- [Compare](examples/compare.json): `areas` containing `area` and `indicators`, plus `meta`.
- [Area Details](examples/area-details.json): `area`, `indicators`, `population_history`, `population_sources`, `meta`.

Browser endpoints are under `/api/v1`, including `/api/v1/status` for readiness. Render continues to use `/health`; both readiness routes share the same handler and response. Source information is embedded, so there is no separate `/sources` endpoint. No map endpoint or suburb-alias lookup is implemented.

## Frontend rules

Use string `sa2_code` identities. Search returns comparable official SA2 names, not semantic or suburb-alias matches. Compare needs two or three unique codes; retain an initial one-area selection locally until another is chosen. Details can describe an ineligible area with its eligibility explanation.

Display indicators in API order: rent, transport, population growth, open space. Format numbers/units but do not recalculate indicators or replace null with zero. Compare and Details use identical indicator objects. Annual history contains counts sorted by actual year, with revision status and source information.

Show dates and make quality/source notes discoverable. Current responses have `meta.publication_ready=true`; the spatial methods are final. No scores are supplied.

Errors are `{ "error": { "code": "...", "message": "..." } }`. Handle 404 for unknown areas, 422 for invalid inputs/selections and 503 with retry. A successful response may contain individual unavailable indicators.

## Update the contract

With backend development dependencies installed, run from the repository root:

```sh
python -m scripts.export_api_contract
python -m pytest backend/tests -q
```

Export runs the app locally without opening a network port or modifying SQLite. Tests check OpenAPI drift. Regenerate examples when data or response behaviour changes; do not maintain different shapes in frontend code.
