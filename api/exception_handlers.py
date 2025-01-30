import sqlite3

import ormar
from asyncpg import UniqueViolationError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from api import get_logger


logger = get_logger(__name__)


async def request_validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
):
    return ORJSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


async def ormar_no_match_exception_handler(
    _: Request,
    exc: ormar.NoMatch,
):
    logger.debug(f"Ormar NoMatch: {exc}")

    return ORJSONResponse(
        status_code=404,
        content={"detail": "Not Found"},
    )


# Create pydantic validation exception handler
async def pydantic_validation_exception_handler(
    _: Request,
    exc: ValidationError,
):
    return ORJSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


# Create asyncpg uniqui validation exception handler
async def unique_validation_exception_handler(
    _: Request,
    exc: UniqueViolationError,
):
    return ORJSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# Create validation exception handler
async def value_exception_handler(
    _: Request,
    exc: ValueError,
):
    return ORJSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# Create Integrity error exception handler
async def sqlite_integrity_error_exception_handler(
    _: Request,
    exc: sqlite3.IntegrityError,
):
    logger.debug(f"DB IntegrityError: {exc}")
    return ORJSONResponse(
        status_code=409,
        content={"detail": "Conflict"},
    )


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        ormar.NoMatch,
        ormar_no_match_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        ValidationError,
        pydantic_validation_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        sqlite3.IntegrityError,
        sqlite_integrity_error_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        ValueError,
        value_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        UniqueViolationError,
        unique_validation_exception_handler,  # type: ignore
    )
