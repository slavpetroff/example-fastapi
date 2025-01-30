import pytest

from api.models.market import Market


_name_counter = 0


@pytest.fixture
def make_market(make_artisan):
    async def make(
        name: str = None,
        address: str = "123 Test Street",
        city: str = "Sofia",
        country: str = "Bulgaria",
        description: str = "Test Market Description",
        owner=None,
        maintainers=None,
    ) -> Market:
        global _name_counter
        if name is None:
            name = f"Test Market {_name_counter}"
            _name_counter += 1

        if owner is None:
            owner = await make_artisan()
        if maintainers is None:
            maintainers = [owner]

        return await Market.objects.create(
            name=name,
            address=address,
            city=city,
            country=country,
            description=description,
            owner=owner,
            maintainers=maintainers,
        )

    return make
