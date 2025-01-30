import pytest

from api.models.user import User


_email_counter = 0


@pytest.fixture
def make_user():
    async def make(
        email: str = None,
        password: str = "testpassword",
    ) -> User:
        global _email_counter
        if email is None:
            email = f"test{_email_counter}@example.com"
            _email_counter += 1

        return await User.objects.create(email=email, password=password)

    return make
