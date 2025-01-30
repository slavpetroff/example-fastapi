import pytest

from api.models.artisan import Artisan


_counter = 0


@pytest.fixture
def make_artisan(make_user):
    async def make(
        name: str = None,
        description: str = "Test Artisan Description",
        phone_no: str = None,
        age: int = 30,
        image_url: str = "https://example.com/image.jpg",
        user=None,
    ) -> Artisan:
        global _counter
        if name is None:
            name = f"Test Artisan {_counter}"
            _counter += 1

        if user is None:
            user = await make_user()

        if not phone_no:
            phone_no = f"+1234567890{_counter}"
            _counter += 1

        return await Artisan.objects.create(
            name=name,
            description=description,
            phone_no=phone_no,
            age=age,
            image_url=image_url,
            user=user,
        )

    return make
