# Ensure all models are imported and registered with the metadata
from api.models.artisan import Artisan
from api.models.category import Category
from api.models.item import Item
from api.models.market import Market
from api.models.tag import Tag
from api.models.user import User


all_models = [
    Artisan,
    Category,
    Item,
    Market,
    Tag,
    User,
]

__all__ = [
    "Artisan",
    "Category",
    "Item",
    "Market",
    "Tag",
    "User",
]
