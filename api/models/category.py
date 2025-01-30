import ormar

from api import db
from api.models.common import DateFieldsMixins


class Category(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="categories",
        constraints=[ormar.IndexColumns("name", unique=True)],
    )

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100, unique=True)
    description = ormar.String(max_length=255)
