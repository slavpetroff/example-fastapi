import ormar

from api import db
from api.models.artisan import Artisan
from api.models.category import Category
from api.models.common import DateFieldsMixins


class Item(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="items",
        constraints=[ormar.IndexColumns("name")],
    )

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100)
    description = ormar.String(max_length=255)
    published = ormar.Boolean(default=False)
    price = ormar.Integer()
    creator = ormar.ForeignKey(
        Artisan,
        related_name="items",
        ondelete="CASCADE",
    )
    categories = ormar.ManyToMany(
        Category,
        related_name="items",
    )
    image_url = ormar.String(max_length=255, nullable=True)
