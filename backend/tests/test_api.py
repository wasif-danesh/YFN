"""Basic API journey and failure tests against the checked-in database.

Tests that change records use temporary copies, never the shared database.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3

import pytest
from fastapi.testclient import TestClient

from backend.app import database
from backend.app.main import create_app
from backend.app.settings import ROOT, Settings

DB = ROOT / "data/greater-melbourne-v1/yfn.sqlite"
CARLTON = "206041117"
FOOTSCRAY = "213031348"


@pytest.fixture
def client():
    before = hashlib.sha256(DB.read_bytes()).hexdigest()
    with TestClient(create_app(Settings(DB))) as client:
        yield client
    assert hashlib.sha256(DB.read_bytes()).hexdigest() == before


def test_health_and_interactive_documentation(client):
    assert client.get("/health").json() == {"status": "ok", "database": "ready"}
    assert client.get("/docs").status_code == 200
    assert "/api/v1/compare" in client.get("/openapi.json").json()["paths"]


def test_search_case_whitespace_order_and_limit(client):
    result = client.get("/api/v1/areas", params={"query": "  cArLtOn ", "limit": 2}).json()
    assert result["areas"][0]["sa2_code"] == CARLTON
    assert len(result["areas"]) == 2
    assert all(a["is_comparable"] for a in result["areas"])
    assert result["meta"]["publication_ready"] is False
    assert len(client.get("/api/v1/areas?limit=1").json()["areas"]) == 1


@pytest.mark.parametrize("query", ["no such neighbourhood", "' OR 1=1 --", "%", "_", "\\"])
def test_search_treats_input_as_literal_text(client, query):
    response = client.get("/api/v1/areas", params={"query": query})
    assert response.status_code == 200
    assert response.json()["areas"] == []


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 51}, {"limit": "bad"}, {"query": "x" * 101}])
def test_search_validation(client, params):
    response = client.get("/api/v1/areas", params=params)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_details_and_compare_share_values_sources_and_order(client):
    details = client.get(f"/api/v1/areas/{CARLTON}").json()
    response = client.get("/api/v1/compare", params={"sa2": f"{FOOTSCRAY},{CARLTON}"})
    assert response.status_code == 200
    compared = response.json()
    assert [a["area"]["sa2_code"] for a in compared["areas"]] == [FOOTSCRAY, CARLTON]
    assert compared["areas"][1]["indicators"] == details["indicators"]
    values = {v["key"]: v for v in details["indicators"]}
    assert list(values) == list(database.INDICATOR_ORDER)
    assert values["rent_weekly"]["raw_value"] == 365
    assert values["rent_weekly"]["reference_period"] == "2021 Census"
    assert values["transport_access"]["score"] is None
    assert values["transport_access"]["quality"]["status"] == "limited"
    for value in values.values():
        assert value["sources"] and value["method_version"]
        assert all(s["roles"] and s["url"] for s in value["sources"])
    assert [p["population"] for p in details["population_history"]] == [20865, 17064, 17942, 21321, 23758, 25267]
    assert [p["year"] for p in details["population_history"]] == list(range(2020, 2026))
    assert details["population_history"][-1]["revision_status"] == "preliminary"
    assert details["population_sources"][0]["source_id"] == "abs-erp-2024-25"
    assert "source_locator" not in json.dumps(details)
    assert "/Users/" not in json.dumps(details)
    assert "pipeline_files_sha256" not in json.dumps(details)


def test_three_area_comparison(client):
    response = client.get("/api/v1/compare", params={"sa2": f"{CARLTON},{FOOTSCRAY},206011106"})
    assert response.status_code == 200
    assert len(response.json()["areas"]) == 3


@pytest.mark.parametrize("selection", ["", CARLTON, f"{CARLTON},{CARLTON}",
    f"{CARLTON},{FOOTSCRAY},206011106,206041127", f"{CARLTON},bad", f"{CARLTON}, {FOOTSCRAY}"])
def test_invalid_comparison(client, selection):
    response = client.get("/api/v1/compare", params={"sa2": selection})
    assert response.status_code == 422
    assert "error" in response.json()


def test_missing_and_repeated_comparison_parameter(client):
    assert client.get("/api/v1/compare").status_code == 422
    assert client.get(f"/api/v1/compare?sa2={CARLTON},{FOOTSCRAY}&sa2={CARLTON},{FOOTSCRAY}").status_code == 422


def test_unknown_malformed_and_ineligible_areas(client):
    assert client.get("/api/v1/areas/not-a-code").status_code == 422
    assert client.get("/api/v1/areas/999999999").status_code == 404
    assert client.get(f"/api/v1/compare?sa2={CARLTON},999999999").status_code == 404
    with database.connect(DB) as db:
        code = db.execute("SELECT sa2_code FROM areas WHERE is_comparable=0 LIMIT 1").fetchone()[0]
    assert client.get(f"/api/v1/areas/{code}").status_code == 200
    response = client.get(f"/api/v1/compare?sa2={CARLTON},{code}")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "AREA_NOT_COMPARABLE"


def test_all_areas_have_serializable_details_and_preserve_nulls(client):
    with database.connect(DB) as db:
        codes = [r[0] for r in db.execute("SELECT sa2_code FROM areas")]
        expected = db.execute("SELECT count(*) FROM observations WHERE raw_value IS NULL").fetchone()[0]
    missing = 0
    for code in codes:
        response = client.get(f"/api/v1/areas/{code}")
        assert response.status_code == 200, (code, response.text)
        details = response.json()
        assert len(details["population_history"]) == 6
        for value in details["indicators"]:
            if value["raw_value"] is None:
                missing += 1
                assert value["quality"]["status"] == "unavailable"
                assert value["quality"]["reason"]
                assert value["score"] is None and value["rating"] is None
    assert missing == expected == 13


@pytest.mark.parametrize("kind", ["missing", "corrupt", "wrong_schema", "bad_manifest"])
def test_unavailable_database_returns_safe_503(tmp_path, kind):
    path = tmp_path / "test.sqlite"
    if kind == "corrupt":
        path.write_text("not a database")
    elif kind == "wrong_schema":
        sqlite3.connect(path).close()
    elif kind == "bad_manifest":
        shutil.copy2(DB, path)
        with sqlite3.connect(path) as db:
            db.execute("UPDATE sample_release SET manifest_json='{}'")
    with TestClient(create_app(Settings(path))) as client:
        for url in ["/health", "/api/v1/areas", f"/api/v1/areas/{CARLTON}"]:
            response = client.get(url)
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
            assert str(tmp_path) not in response.text and "SELECT" not in response.text
    if kind == "missing":
        assert not path.exists()


def test_missing_indicator_is_failure_not_silent_partial_success(tmp_path):
    path = tmp_path / "test.sqlite"
    shutil.copy2(DB, path)
    with sqlite3.connect(path) as db:
        # Drop a leaf value with foreign keys disabled only in this disposable fixture.
        db.execute("DELETE FROM observations WHERE sa2_code=? AND indicator_key='rent_weekly'", (CARLTON,))
    with TestClient(create_app(Settings(path))) as client:
        assert client.get(f"/api/v1/areas/{CARLTON}").status_code == 503


def test_runtime_database_is_readonly():
    with database.connect(DB) as db:
        with pytest.raises(sqlite3.OperationalError):
            db.execute("UPDATE areas SET name='changed'")


def test_cors_and_unsupported_write(client):
    allowed = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    denied = client.get("/health", headers={"Origin": "https://unapproved.example"})
    assert "access-control-allow-origin" not in denied.headers
    preflight = client.options("/api/v1/areas", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert preflight.status_code == 200
    write = client.post("/api/v1/areas", json={})
    assert write.status_code == 405
    assert write.headers["allow"] == "GET"


def test_settings_resolve_from_repo_not_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_PATH", "data/greater-melbourne-v1/yfn.sqlite")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", '["https://frontend.example"]')
    settings = Settings.from_environment()
    assert settings.database_path == DB
    assert settings.cors_allowed_origins == ("https://frontend.example",)


@pytest.mark.parametrize("origins", ['*', '"http://localhost:3000"', '["*"]', '[1]', '["https://example.com/path"]'])
def test_invalid_cors_configuration(monkeypatch, origins):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", origins)
    with pytest.raises(ValueError, match="CORS_ALLOWED_ORIGINS"):
        Settings.from_environment()


def test_openapi_export_matches_application(client):
    saved = json.loads((ROOT / "contracts/openapi.json").read_text())
    assert client.get("/openapi.json").json() == saved
