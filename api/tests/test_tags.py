from http import HTTPStatus


async def test_create_tag(client, make_item, make_artisan):
    item = await make_item()
    artisan = await make_artisan()
    new_tag_data = {
        "name": "New Test Tag",
        "item_id": item.id,
        "created_by_id": artisan.id,
    }

    response = await client.post("/api/tags/", json=new_tag_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["name"] == new_tag_data["name"]
    assert data["item"]["id"] == new_tag_data["item_id"]


async def test_get_tag(client, make_tag):
    tag = await make_tag()

    response = await client.get(f"/api/tags/{tag.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json()["id"] == tag.id


async def test_list_tags(client, make_tag):
    tag = await make_tag()

    response = await client.get("/api/tags/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert len(response.json()) >= 1
    assert any(t["id"] == tag.id for t in response.json()["items"])


async def test_get_nonexistent_tag(client):
    response = await client.get("/api/tags/99999/")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


async def test_create_tag_invalid_data(client):
    invalid_data = {
        "name": "",  # Empty name
    }
    response = await client.post("/api/tags/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
