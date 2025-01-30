from contextlib import asynccontextmanager

import databases
import sqlalchemy
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from api import db, get_logger
from api.config import settings
from api.exception_handlers import include_exception_handlers
from api.middleware import ErrorLoggingMiddleware
from api.routers import artisan, category, health, item, market, tag, user
from api.tasks.brokers import broker
from api.utils.tracing import metrics, setup_tracing


logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Application")

    database = app.state.database
    if not database.is_connected:
        await database.connect()

    await broker.connect()

    yield

    await broker.close()

    if database.is_connected:
        await database.disconnect()

    logger.info("Stopping Application")


def create_app(
    engine: sqlalchemy.engine.Engine | None = None,
    metadata: sqlalchemy.MetaData | None = None,
    database: databases.Database | None = None,
) -> FastAPI:
    debug = settings.ENV == "test"
    service_name = "api"

    app = FastAPI(
        debug=debug,
        title="API",
        version="0.1.0",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    engine = engine or db.base_ormar_config.engine
    metadata = metadata or db.base_ormar_config.metadata
    database = database or db.base_ormar_config.database

    app.state.engine = engine
    app.state.metadata = metadata
    app.state.database = database

    setup_tracing(
        broker=broker,
        service_name=service_name,
        app=app,
    )

    include_exception_handlers(app)

    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(user.router, prefix="/api", tags=["user"])
    app.include_router(artisan.router, prefix="/api", tags=["artisan"])
    app.include_router(category.router, prefix="/api", tags=["category"])
    app.include_router(tag.router, prefix="/api", tags=["tag"])
    app.include_router(item.router, prefix="/api", tags=["item"])
    app.include_router(market.router, prefix="/api", tags=["market"])

    app.add_route("/metrics", metrics)

    app.add_middleware(ErrorLoggingMiddleware)

    add_pagination(app)

    return app
