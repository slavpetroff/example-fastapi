import pytest

from api.models.tag import Tag


_name_counter = 0


@pytest.fixture
def make_tag(make_item, make_artisan):
    async def make(name: str = None, item=None, created_by=None) -> Tag:
        global _name_counter
        if name is None:
            name = f"Test Tag {_name_counter}"
            _name_counter += 1

        if item is None:
            item = await make_item()
        if created_by is None:
            created_by = await make_artisan()

        return await Tag.objects.create(
            name=name,
            item=item,
            created_by=created_by,
        )

    return make
