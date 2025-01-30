import ormar

from api import db
from api.models.common import DateFieldsMixins
from api.models.user import User


class Artisan(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="artisans",
        constraints=[ormar.IndexColumns("name", unique=True)],
    )

    id = ormar.Integer(primary_key=True)
    description = ormar.String(max_length=255)
    image_url = ormar.String(max_length=255, nullable=True)
    name = ormar.String(max_length=100, unique=True)

    phone_no = ormar.String(max_length=15, nullable=True, unique=True)
    age = ormar.Integer(nullable=True)

    user = ormar.ForeignKey(User, related_name="artisans", ondelete="CASCADE")
