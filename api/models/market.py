from typing import Optional

import ormar

from api import db
from api.models.artisan import Artisan
from api.models.common import DateFieldsMixins


class MarketMaintainer(ormar.Model):
    ormar_config = db.base_ormar_config.copy(
        tablename="market_maintainers",
    )

    id = ormar.Integer(primary_key=True)
    created_at = ormar.DateTime()
    updated_at = ormar.DateTime()


class Market(ormar.Model, DateFieldsMixins):
    ormar_config = db.base_ormar_config.copy(
        tablename="market",
        constraints=[
            ormar.IndexColumns("name", unique=True),
            ormar.IndexColumns("city"),
        ],
    )

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100, unique=True)
    address = ormar.String(max_length=100, nullable=True)
    city = ormar.String(max_length=32)
    country = ormar.String(max_length=32, default="Bulgaria")
    owner: Optional[Artisan] = ormar.ForeignKey(
        Artisan,
        nullable=True,
        related_name="own_market",
    )
    maintainers: list[Artisan] = ormar.ManyToMany(
        Artisan,
        related_name="markets",
        through=MarketMaintainer,
    )
    description = ormar.String(max_length=255, nullable=True)
