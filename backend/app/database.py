"""Read-only SQLite access; no ORM or GIS dependencies are needed at runtime."""
from contextlib import contextmanager
import json
import sqlite3

from .models import Meta

INDICATOR_ORDER = ("rent_weekly", "transport_access", "population_growth", "green_space_per_resident")
EXPLANATIONS = {
    "rent_weekly": "Median weekly rent reported in the 2021 Census; not current advertised rent.",
    "transport_access": "Area-level transport access over covered land; not a commute time or access from a property.",
    "population_growth": "Historical estimated population change, not a forecast. 2025 estimates are preliminary.",
    "green_space_per_resident": "Selected open space per resident; not walking access, park quality or confirmed vegetation.",
}


class DatabaseUnavailable(Exception):
    """Converted to a safe HTTP 503 by the application."""


@contextmanager
def connect(path):
    # mode=ro also prevents silently creating an empty DB for a mistyped path.
    db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, check_same_thread=False, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")  # Keep all queries in one response on the same snapshot.
        yield db
    finally:
        db.close()


def metadata(db):
    rows = db.execute("SELECT release_id,data_mode,publication_ready,manifest_json FROM sample_release").fetchall()
    if len(rows) != 1:
        raise DatabaseUnavailable("Expected one dataset manifest")
    row = rows[0]
    try:
        manifest = json.loads(row["manifest_json"])
        if (row["release_id"] != manifest["release_id"] or row["data_mode"] != manifest["data_mode"]
                or bool(row["publication_ready"]) != manifest["publication_ready"]):
            raise ValueError("Inconsistent dataset metadata")
        return Meta(data_mode=manifest["data_mode"], data_version=manifest["release_id"],
                    method_version=manifest["method_version"], boundary_year=manifest["boundary_year"],
                    publication_ready=manifest["publication_ready"],
                    benchmark_count=manifest["transport_benchmark_count"])
    except (ValueError, KeyError, TypeError) as exc:
        raise DatabaseUnavailable("Invalid dataset metadata") from exc


def validate(db):
    """Cheap readiness check for this small database, including required tables."""
    metadata(db)
    if db.execute("PRAGMA quick_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchone():
        raise DatabaseUnavailable("Database integrity failed")
    # Explicit columns ensure incompatible databases fail before serving a page.
    for sql in (
        "SELECT sa2_code,name,boundary_year,is_comparable,eligibility_note FROM areas",
        "SELECT sa2_code,indicator_key,raw_value,score,rating,reference_period,start_year,end_year,quality_status,quality_note,coverage_fraction,method_id FROM observations",
        "SELECT indicator_key,label,unit FROM indicators",
        "SELECT method_id,approval_status FROM methods",
        "SELECT sa2_code,indicator_key,source_id,role FROM observation_sources",
        "SELECT source_id,publisher,dataset_name,url,reference_period,boundary_year,observation_date,licence,limitation FROM data_sources",
        "SELECT sa2_code,year,population,reference_date,revision_status,source_id FROM population_history",
    ):
        db.execute(sql + " LIMIT 0")
    if not db.execute("SELECT 1 FROM areas LIMIT 1").fetchone():
        raise DatabaseUnavailable("Empty area table")
    if db.execute("""SELECT a.sa2_code FROM areas a LEFT JOIN observations o USING(sa2_code)
        GROUP BY a.sa2_code HAVING count(o.indicator_key) != 4 LIMIT 1""").fetchone():
        raise DatabaseUnavailable("Incomplete indicator coverage")
    if db.execute("""SELECT a.sa2_code FROM areas a LEFT JOIN population_history p USING(sa2_code)
        GROUP BY a.sa2_code HAVING count(p.year) = 0 LIMIT 1""").fetchone():
        raise DatabaseUnavailable("Missing population history")


def area_value(row):
    return {"sa2_code": row["sa2_code"], "name": row["name"], "boundary_year": row["boundary_year"],
            "geography_type": "SA2", "is_comparable": bool(row["is_comparable"]),
            "eligibility_note": row["eligibility_note"]}


def search(db, query, limit):
    # Treat user-entered %, _ and backslashes as literal characters, not LIKE operators.
    term = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = db.execute("""SELECT * FROM areas WHERE is_comparable=1 AND name LIKE ? ESCAPE '\\'
        ORDER BY CASE WHEN name = ? COLLATE NOCASE THEN 0
                      WHEN name LIKE ? ESCAPE '\\' THEN 1 ELSE 2 END,
                 name COLLATE NOCASE, sa2_code LIMIT ?""", (f"%{term}%", query, f"{term}%", limit))
    return [area_value(row) for row in rows]


def get_area(db, code):
    row = db.execute("SELECT * FROM areas WHERE sa2_code=?", (code,)).fetchone()
    return area_value(row) if row else None


def indicators(db, area):
    rows = db.execute("""SELECT o.*,i.label,i.unit,m.approval_status FROM observations o
        JOIN indicators i USING(indicator_key) JOIN methods m ON m.method_id=o.method_id
        WHERE o.sa2_code=?""", (area["sa2_code"],)).fetchall()
    by_key = {row["indicator_key"]: row for row in rows}
    if set(by_key) != set(INDICATOR_ORDER):
        raise DatabaseUnavailable("Incomplete indicator records")
    result = []
    for key in INDICATOR_ORDER:
        row = by_key[key]
        sources = {}
        for source in db.execute("""SELECT s.*,os.role FROM data_sources s JOIN observation_sources os
            USING(source_id) WHERE os.sa2_code=? AND os.indicator_key=? ORDER BY s.source_id,os.role""",
                                 (area["sa2_code"], key)):
            value = dict(source)
            role = value.pop("role")
            sources.setdefault(value["source_id"], {**value, "roles": []})["roles"].append(role)
        if not sources:
            raise DatabaseUnavailable("Missing indicator provenance")
        result.append({"key": key, "label": row["label"], "unit": row["unit"],
                       "raw_value": row["raw_value"], "score": row["score"], "rating": row["rating"],
                       "reference_period": row["reference_period"], "start_year": row["start_year"],
                       "end_year": row["end_year"], "method_version": row["method_id"],
                       "method_status": row["approval_status"], "explanation": EXPLANATIONS[key],
                       "geography": {"type": "SA2", "code": area["sa2_code"], "boundary_year": area["boundary_year"]},
                       "quality": {"status": row["quality_status"], "reason": row["quality_note"],
                                   "coverage_fraction": row["coverage_fraction"]}, "sources": list(sources.values())})
    return result


def population_history(db, code):
    rows = db.execute("""SELECT year,population,reference_date,revision_status,source_id
        FROM population_history WHERE sa2_code=? ORDER BY year""", (code,))
    return [dict(row) for row in rows]


def population_sources(db, code):
    rows = db.execute("""SELECT DISTINCT s.* FROM data_sources s JOIN population_history p USING(source_id)
        WHERE p.sa2_code=? ORDER BY s.source_id""", (code,))
    return [dict(row) for row in rows]
