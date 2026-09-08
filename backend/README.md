# Backend workspace

Reserved for the FastAPI REST service. Application code, dependency manifests and response models have not been created yet. See the root [README](../README.md#local-application-development).

Create `app/main.py` as the ASGI entry point, with `app/api/` for routes, `app/schemas/` for response models, `app/repositories/` for parameterized read-only SQLite access, `app/services/` for composition, and `app/core/` for configuration. Create package `__init__.py` files as needed and keep tests in `tests/`.

Commands run from the repository root. Resolve `DATABASE_PATH` against that root and open SQLite using a read-only URI (`mode=ro`). Validate the database on startup and make `/health` fail when it cannot be used. Read data-mode/release metadata from the database; do not turn a sample into production data by changing an environment variable.

Use separate pinned `requirements.txt` (runtime) and `requirements-dev.txt` (including runtime and tests). GIS libraries belong to the pipeline environment, not the deployed API. For the documented development command, include Uvicorn's dotenv support, for example through `uvicorn[standard]`.
