from http import HTTPStatus


async def test_create_market(client, make_artisan):
    artisan = await make_artisan()
    new_market_data = {
        "name": "New Test Market",
        "address": "456 New Street",
        "city": "New City",
        "country": "New Country",
        "description": "New Market Description",
        "owner_id": artisan.id,
        "maintainer_ids": [artisan.id],
    }

    response = await client.post("/api/markets/", json=new_market_data)
    assert response.status_code == HTTPStatus.CREATED, response.text
    data = response.json()
    assert data["name"] == new_market_data["name"]
    assert data["description"] == new_market_data["description"]


async def test_get_market(client, make_market):
    market = await make_market()

    response = await client.get(f"/api/markets/{market.id}/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json()["id"] == market.id


async def test_list_markets(client, make_market):
    market = await make_market()

    response = await client.get("/api/markets/")
    assert response.status_code == HTTPStatus.OK, response.text
    assert len(response.json()["items"]) >= 1
    assert any(m["id"] == market.id for m in response.json()["items"])


async def test_get_nonexistent_market(client):
    response = await client.get("/api/markets/99999/")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.text


async def test_create_market_invalid_data(client):
    invalid_data = {
        "name": "",  # Empty name
        "description": "Test Description",
    }
    response = await client.post("/api/markets/", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
