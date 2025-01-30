from http import HTTPStatus


async def test_create_item(client, make_artisan, make_category):
    artisan = await make_artisan()
    category = await make_category()

    new_item_data = {
        "name": "New Test Item",
        "description": "New Test Item Description",
        "published": True,
        "price": 2000,
        "image_url": "https://example.com/new-item.jpg",
        "creator_id": artisan.id,
        "category_ids": [category.id],
    }

    response = await client.post("/api/items/", json=new_item_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["name"] == new_item_data["name"]
    assert data["price"] == new_item_data["price"]
    assert data["published"] == new_item_data["published"]
    assert data["categories"][0]["id"] == new_item_data["category_ids"][0]


async def test_get_item(client, make_item):
    item = await make_item()

    response = await client.get(f"/api/items/{item.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert data["id"] == item.id, response.text
    assert "creator" in data, response.text
    assert "categories" in data, response.text


async def test_list_items(client, make_item):
    item = await make_item()

    response = await client.get("/api/items/")
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()["items"]
    assert len(data) >= 1, response.text
    assert any(i["id"] == item.id for i in data), response.text


async def test_update_item(client, make_item, make_category):
    item = await make_item()
    await make_category()

    update_data = {
        "name": "Updated Item Name",
        "price": 2500,
        "published": True,
        "creator_id": item.creator.id,
        "description": "Updated Item Description",
        "category_ids": [category.id for category in item.categories],
    }

    response = await client.patch(f"/api/items/{item.id}/", json=update_data)
    assert response.status_code == HTTPStatus.OK, response.text
    data = response.json()
    assert data["name"] == update_data["name"], response.text
    assert data["price"] == update_data["price"], response.text
    assert data["published"] == update_data["published"], response.text


async def test_delete_item(client, make_item):
    item = await make_item()

    response = await client.delete(f"/api/items/{item.id}/")
    assert response.status_code == HTTPStatus.NO_CONTENT, response.text

    # Verify item is deleted
    get_response = await client.get(f"/api/items/{item.id}/")
    assert get_response.status_code == HTTPStatus.NOT_FOUND, get_response.text


async def test_create_item_invalid_data(client):
    invalid_data = {
        "name": "",
        "price": -100,  # Invalid price
    }
    response = await client.post("/api/items/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
