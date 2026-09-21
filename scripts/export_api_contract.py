"""Run from the repo root: python -m scripts.export_api_contract.

Exports OpenAPI and real response examples for frontend development, without a server.
Requires backend development dependencies. Never changes the database.
"""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import ROOT, Settings


def main():
    target = ROOT / "contracts"
    examples = target / "examples"
    examples.mkdir(exist_ok=True)
    app = create_app(Settings(ROOT / "data/greater-melbourne-v1/yfn.sqlite"))
    (target / "openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")
    with TestClient(app) as client:
        for name, url in {
            "search": "/api/v1/areas?query=carl",
            "compare": "/api/v1/compare?sa2=206041117,213031348",
            "area-details": "/api/v1/areas/206041117",
        }.items():
            response = client.get(url)
            response.raise_for_status()
            (examples / f"{name}.json").write_text(json.dumps(response.json(), indent=2) + "\n")
    print("Updated contracts/openapi.json and three response examples.")


if __name__ == "__main__":
    main()
