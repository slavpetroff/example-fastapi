import ormar
from databases import Database
from sqlalchemy import MetaData, create_engine

from api.config import settings


engine = create_engine(
    settings.DATABASE.URL,
    echo=True,
)
database = Database(settings.DATABASE.URL)
metadata = MetaData()
base_ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
    engine=engine,
)
