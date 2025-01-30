from http import HTTPStatus


async def test_create_artisan(client, make_user):
    # Use existing user from test data
    user = await make_user("test_create_Artisan@example.com", "testpassword")

    new_artisan_data = {
        "name": "New Test Artisan",
        "description": "New Test Artisan Description",
        "phone_no": "+9876543210",
        "age": 35,
        "image_url": "https://example.com/new-image.jpg",
        "user_id": user.id,
    }

    response = await client.post("/api/artisans/", json=new_artisan_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["name"] == new_artisan_data["name"]
    assert data["description"] == new_artisan_data["description"]
    assert data["user"]["id"] == new_artisan_data["user_id"]


async def test_get_artisan(client, make_artisan):
    artisan = await make_artisan()

    response = await client.get(f"/api/artisans/{artisan.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json()["id"] == artisan.id


async def test_list_artisans(client, make_artisan):
    artisan = await make_artisan()

    response = await client.get("/api/artisans/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert len(response.json()) >= 1
    assert any(a["id"] == artisan.id for a in response.json()["items"])


async def test_get_nonexistent_artisan(client):
    response = await client.get("/api/artisans/99999/")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


async def test_create_artisan_invalid_data(client):
    invalid_data = {
        "name": "",  # Empty name
        "description": "Test Description",
    }
    response = await client.post("/api/artisans/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
