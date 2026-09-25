"""The shared JSON contract used by both Compare and Area Details."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Meta(Model):
    data_mode: Literal["real"]
    data_version: str
    method_version: str
    boundary_year: int
    publication_ready: bool
    benchmark_count: int | None


class Area(Model):
    sa2_code: str = Field(pattern=r"^[0-9]{9}$")
    name: str
    boundary_year: int
    geography_type: Literal["SA2"] = "SA2"
    is_comparable: bool
    eligibility_note: str


class Source(Model):
    source_id: str
    publisher: str
    dataset_name: str
    url: str
    reference_period: str
    boundary_year: int | None
    observation_date: date | None
    licence: str
    limitation: str


class IndicatorSource(Source):
    roles: list[str]


class Quality(Model):
    status: Literal["available", "limited", "unavailable"]
    reason: str
    coverage_fraction: float | None = Field(ge=0, le=1)


class Geography(Model):
    type: Literal["SA2"] = "SA2"
    code: str
    boundary_year: int


class IndicatorValue(Model):
    key: Literal["rent_weekly", "transport_access", "population_growth", "green_space_per_resident"]
    label: str
    unit: str
    raw_value: float | None
    score: float | None = Field(ge=0, le=100)
    rating: str | None
    reference_period: str
    start_year: int | None
    end_year: int | None
    method_version: str
    method_status: Literal["source_definition", "approved"]
    explanation: str
    geography: Geography
    quality: Quality
    sources: list[IndicatorSource]


class AreaIndicators(Model):
    area: Area
    indicators: list[IndicatorValue]


class PopulationPoint(Model):
    year: int
    population: int | None = Field(ge=0)
    reference_date: date
    revision_status: Literal["final", "revised", "preliminary"]
    source_id: str


class SearchResponse(Model):
    areas: list[Area]
    meta: Meta


class CompareResponse(Model):
    areas: list[AreaIndicators]
    meta: Meta


class DetailsResponse(AreaIndicators):
    population_history: list[PopulationPoint]
    population_sources: list[Source]
    meta: Meta


class HealthResponse(Model):
    status: Literal["ok"] = "ok"
    database: Literal["ready"] = "ready"


class Error(Model):
    code: str
    message: str


class ErrorResponse(Model):
    error: Error
