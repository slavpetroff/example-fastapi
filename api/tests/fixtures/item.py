from typing import Optional

import pytest

from api.models.item import Item


_name_counter = 0


@pytest.fixture
def make_item(make_artisan, make_category):
    async def make(
        name: str = None,
        description: str = "Test Item Description",
        published: bool | None = None,
        price: int = 1000,
        image_url: str = "https://example.com/image.jpg",
        categories: Optional[list[int]] = None,
        creator=None,
    ) -> Item:
        global _name_counter
        if name is None:
            name = f"Test Item {_name_counter}"
            _name_counter += 1

        if not published:
            published = False

        if not creator:
            creator = await make_artisan()

        if not categories:
            categories = await make_category()

        return await Item.objects.create(
            name=name,
            description=description,
            published=published if published is not None else False,
            price=price,
            image_url=image_url,
            creator=creator,
            categories=categories,
        )

    return make
