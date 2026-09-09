"""App setup. Run: python -m uvicorn backend.app.main:app --reload"""
from contextlib import asynccontextmanager
import logging
import sqlite3

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from . import database
from .api import router
from .settings import Settings

logger = logging.getLogger(__name__)


def error_response(status, code, message, headers=None):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}}, headers=headers)


def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(app):
        try:
            with database.connect(settings.database_path) as db:
                database.validate(db)
        except (sqlite3.Error, database.DatabaseUnavailable):
            # Keep /health reachable with a 503; each request rechecks readiness.
            logger.exception("Database unavailable at startup")
        yield

    app = FastAPI(title="Your Friendly Neighbourhood API", version="1.0.0", lifespan=lifespan,
                  description="Read-only Greater Melbourne data. Spatial measures remain provisional; inspect meta and quality notes.")
    app.state.settings = settings
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_allowed_origins),
                       allow_methods=["GET"], allow_headers=["Accept", "Content-Type"], allow_credentials=False)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc):
        return error_response(422, "INVALID_REQUEST", "Check the area codes, query length and result limit.")

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc):
        if isinstance(exc.detail, dict):
            return error_response(exc.status_code, exc.detail["code"], exc.detail["message"], exc.headers)
        return error_response(exc.status_code, "HTTP_ERROR", str(exc.detail), exc.headers)

    async def unavailable(request: Request, exc):
        logger.error("Unable to serve database response", exc_info=exc)
        return error_response(503, "DATABASE_UNAVAILABLE", "Area data is temporarily unavailable. Please try again.")

    app.add_exception_handler(sqlite3.Error, unavailable)
    app.add_exception_handler(database.DatabaseUnavailable, unavailable)
    app.add_exception_handler(ResponseValidationError, unavailable)
    app.include_router(router)
    return app


app = create_app()
