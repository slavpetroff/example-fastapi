import ormar
import pytest
from databases import Database
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from api import db
from api.main import create_app, lifespan
from api.models import all_models
from api.tests.fixtures import *  # noqa


@pytest.fixture(scope="session")
def postgres_container():
    """Fixture to start a PostgreSQL container"""
    with PostgresContainer("postgres:latest") as container:
        yield container


@pytest.fixture(scope="session")
async def setup_database(postgres_container):
    """Fixture to set up the test database using a PostgreSQL container"""
    test_db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://",
        "postgresql+asyncpg://",
    )
    test_db = Database(test_db_url)
    test_engine = create_async_engine(test_db_url)
    test_metadata = db.base_ormar_config.metadata
    test_metadata.bind = test_engine
    new_ormar = ormar.OrmarConfig(
        database=test_db,
        metadata=test_metadata,
        engine=test_engine,
    )

    # Bind the new configuration
    db.base_ormar_config = new_ormar
    db.database = test_db
    db.engine = test_engine
    db.metadata = test_metadata

    # Create a synchronous engine for migrations
    sync_engine = create_engine(test_db_url.replace("asyncpg", "psycopg2"))

    # Temporarily bind metadata to the sync engine for DDL operations
    test_metadata.bind = sync_engine

    # Drop all tables before tests using the synchronous engine
    async with test_db:
        test_metadata.drop_all(sync_engine)

    # Create all tables using the synchronous engine
    async with test_db:
        test_metadata.create_all(sync_engine)

    # Revert metadata binding to the asynchronous engine
    test_metadata.bind = test_engine

    yield


@pytest.fixture(scope="session")
async def apply_models_config(setup_database):
    """Fixture to apply models' metadata, engine, and database."""
    original_configs = {}
    for model in all_models:
        if (
            isinstance(model, type)
            and issubclass(model, ormar.Model)
            and hasattr(model, "ormar_config")
        ):
            # Save original config
            original_configs[model] = {
                "metadata": model.ormar_config.metadata,
                "database": model.ormar_config.database,
                "engine": model.ormar_config.engine,
            }
            # Apply new config
            model.ormar_config.metadata = db.metadata
            model.ormar_config.database = db.database
            model.ormar_config.engine = db.engine

    yield


@pytest.fixture()
async def client(apply_models_config):
    app = create_app()

    async with (
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client,
        lifespan(app=app),
    ):
        yield test_client
