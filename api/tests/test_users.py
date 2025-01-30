from http import HTTPStatus


async def test_create_user(client):
    new_user_data = {
        "email": "newuser@example.com",
        "password": "newuserpassword",
    }

    response = await client.post("/api/users/", json=new_user_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["email"] == new_user_data["email"]
    # Password should not be returned in response
    assert "password" not in data


async def test_get_user(client, make_user):
    user = await make_user()

    response = await client.get(f"/api/users/{user.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json()["id"] == user.id
    assert "password" not in response.json()


async def test_list_users(client, make_user):
    user = await make_user()

    response = await client.get("/api/users/")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert len(data["items"]) >= 1
    assert any(u["id"] == user.id for u in data["items"])
    assert all("password" not in u for u in data["items"])


async def test_list_users_pagination(client, make_user):
    # Create multiple users for pagination testing
    users = []
    for i in range(15):
        users.append(
            await make_user(
                email=f"test_pagination_{i}@example.com",
                password="testpassword",
            ),
        )

    # Test first page
    response = await client.get("/api/users/?size=5")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] >= 15
    assert data["page"] == 1
    assert data["size"] == 5
    assert data["pages"] >= 3

    # Test second page
    response = await client.get("/api/users/?size=5&page=2")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2

    # Test last page
    response = await client.get(f"/api/users/?size=5&page={data['pages']}")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert len(data["items"]) > 0
    assert data["page"] == data["pages"]


async def test_pagination_across_multiple_pages(client, make_user):
    # Create a set of users
    users = []
    for i in range(10):
        users.append(
            await make_user(
                email=f"test_multiple_pages_{i}@example.com",
                password="testpassword",
            ),
        )

    # Get all users using pagination
    all_users = set()
    page = 1
    while True:
        response = await client.get(f"/api/users/?size=3&page={page}")
        assert response.status_code == HTTPStatus.OK, response.text
        data = response.json()

        if not data["items"]:
            break

        for user in data["items"]:
            all_users.add(user["id"])

        page += 1

    # Verify all created users are found
    assert all(user.id in all_users for user in users)


async def test_large_dataset_pagination(client, make_user):
    # Create a larger dataset
    users = []
    for i in range(50):
        users.append(
            await make_user(
                email=f"test_large_dataset_{i}@example.com",
                password="testpassword",
            ),
        )

    # Test different page sizes
    for page_size in [10, 20, 30]:
        response = await client.get(f"/api/users/?size={page_size}")
        assert response.status_code == HTTPStatus.OK, response.text
        data = response.json()
        assert len(data["items"]) == page_size
        assert data["total"] >= 50

    # Test last page with different size
    response = await client.get("/api/users/?size=30&page=2")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert len(data["items"]) > 0
    assert data["page"] == 2


async def test_get_nonexistent_user(client):
    response = await client.get("/api/users/99999/")
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_create_user_invalid_data(client):
    invalid_data = {
        "email": "invalid-email",  # Invalid email format
        "password": "",  # Empty password
    }

    response = await client.post("/api/users/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_create_duplicate_user(client, make_user):
    # Create first user
    email = "test_duplicate@example.com"
    await make_user(email=email, password="testpassword")

    # Try to create another user with the same email
    duplicate_user_data = {
        "email": email,
        "password": "anotherpassword",
    }

    response = await client.post("/api/users/", json=duplicate_user_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
