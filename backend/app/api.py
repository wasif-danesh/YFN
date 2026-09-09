"""Website endpoints and the hosting health check."""
import re
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from . import database
from .models import CompareResponse, DetailsResponse, ErrorResponse, HealthResponse, SearchResponse

router = APIRouter(responses={422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})


def get_db(request: Request):
    with database.connect(request.app.state.settings.database_path) as db:
        database.validate(db)
        yield db


Db = Annotated[sqlite3.Connection, Depends(get_db)]


def require_area(db, code):
    area = database.get_area(db, code)
    if area is None:
        raise HTTPException(404, detail={"code": "AREA_NOT_FOUND", "message": "That area was not found."})
    return area


@router.get("/api/v1/status", response_model=HealthResponse, tags=["Health"])
@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health(db: Db):
    """Technical readiness only; publication approval is reported separately in data meta."""
    return HealthResponse()


@router.get("/api/v1/areas", response_model=SearchResponse, tags=["Areas"])
def search_areas(db: Db, query: Annotated[str, Query(max_length=100)] = "",
                 limit: Annotated[int, Query(ge=1, le=50)] = 20):
    """Search comparable official SA2 names; an empty query lists names alphabetically."""
    return {"areas": database.search(db, query.strip(), limit), "meta": database.metadata(db)}


@router.get("/api/v1/compare", response_model=CompareResponse,
            responses={404: {"model": ErrorResponse}}, tags=["Areas"])
def compare_areas(request: Request, db: Db, sa2: Annotated[str, Query(max_length=29)]):
    """Compare two or three distinct eligible codes, preserving the requested order."""
    codes = sa2.split(",")
    if (len(request.query_params.getlist("sa2")) != 1 or len(codes) not in (2, 3)
            or len(set(codes)) != len(codes) or any(not re.fullmatch(r"[0-9]{9}", code) for code in codes)):
        raise HTTPException(422, detail={"code": "INVALID_SELECTION", "message": "Choose two or three different nine-digit SA2 codes."})
    areas = [require_area(db, code) for code in codes]
    if any(not area["is_comparable"] for area in areas):
        raise HTTPException(422, detail={"code": "AREA_NOT_COMPARABLE", "message": "One of these areas is not eligible for comparison."})
    return {"areas": [{"area": area, "indicators": database.indicators(db, area)} for area in areas],
            "meta": database.metadata(db)}


@router.get("/api/v1/areas/{sa2_code}", response_model=DetailsResponse,
            responses={404: {"model": ErrorResponse}}, tags=["Areas"])
def area_details(db: Db, sa2_code: Annotated[str, Path(pattern=r"^[0-9]{9}$")]):
    """Area indicators and annual population counts, including source and revision notes."""
    area = require_area(db, sa2_code)
    return {"area": area, "indicators": database.indicators(db, area),
            "population_history": database.population_history(db, sa2_code),
            "population_sources": database.population_sources(db, sa2_code), "meta": database.metadata(db)}
