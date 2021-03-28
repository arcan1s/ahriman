from pytest_aiohttp import TestClient


async def test_get(client: TestClient) -> None:
    """
    must generate status page correctly (/)
    """
    response = await client.get("/")
    assert response.status == 200
    assert await response.text()


async def test_get_index(client: TestClient) -> None:
    """
    must generate status page correctly (/index.html)
    """
    response = await client.get("/index.html")
    assert response.status == 200
    assert await response.text()
