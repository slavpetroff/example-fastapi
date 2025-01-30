import ormar

from api import db
from api.models.artisan import Artisan
from api.models.common import DateFieldsMixins
from api.models.item import Item


class Tag(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="tags",
        constraints=[ormar.IndexColumns("name", unique=True)],
    )

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100, unique=True)
    item = ormar.ForeignKey(
        Item,
        related_name="tags",
        ondelete="CASCADE",
    )

    created_by = ormar.ForeignKey(
        Artisan,
        related_name="tags",
        ondelete="CASCADE",
    )
