# Shared API contract

Agree response models before parallel API/UI development. Start with the [contract proposal](../docs/data-and-api.md#5-rest-contract-proposal) and the [real schema](../data/samples/greater-melbourne-v1/schema-guide.md).

Once FastAPI models exist, export their OpenAPI schema to `openapi.json` and keep reviewed examples in `examples/`. Generate the schema from the running application rather than editing two competing definitions. Contract tests should check examples against those models and CI should detect a stale export.

Both real and synthetic responses must include the same fields for identity, value, units, period, quality, coverage and provenance. Preserve nulls and nine-digit SA2 strings. Document breaking changes and update the UI and API in the same pull request; maintain compatibility during their separate Render deployments.
