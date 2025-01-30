import pytest

from api.models.category import Category


_name_counter = 0


@pytest.fixture
def make_category():
    async def make(
        name: str = None,
        description: str = "Test Category Description",
    ) -> Category:
        global _name_counter
        if name is None:
            name = f"Test Category {_name_counter}"
            _name_counter += 1

        return await Category.objects.create(
            name=name,
            description=description,
        )

    return make
