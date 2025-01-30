from http import HTTPStatus


async def test_create_category(client):
    new_category_data = {
        "name": "New Test Category",
        "description": "New Test Category Description",
    }

    response = await client.post("/api/categories/", json=new_category_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["name"] == new_category_data["name"]
    assert data["description"] == new_category_data["description"]


async def test_get_category(client, make_category):
    category = await make_category()

    response = await client.get(f"/api/categories/{category.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json()["id"] == category.id


async def test_list_categories(client, make_category):
    category = await make_category()

    response = await client.get("/api/categories/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert len(response.json()) >= 1
    assert any(c["id"] == category.id for c in response.json()["items"])


async def test_get_nonexistent_category(client):
    response = await client.get("/api/categories/99999/")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


async def test_create_category_invalid_data(client):
    invalid_data = {
        "name": "",  # Empty name
    }
    response = await client.post("/api/categories/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
