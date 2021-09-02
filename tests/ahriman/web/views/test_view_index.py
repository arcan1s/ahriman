from pytest_aiohttp import TestClient


async def test_get(client_with_auth: TestClient) -> None:
    """
    must generate status page correctly (/)
    """
    response = await client_with_auth.get("/")
    assert response.status == 200
    assert await response.text()


async def test_get_index(client_with_auth: TestClient) -> None:
    """
    must generate status page correctly (/index.html)
    """
    response = await client_with_auth.get("/index.html")
    assert response.status == 200
    assert await response.text()


async def test_get_without_auth(client: TestClient) -> None:
    """
    must use dummy authorized_userid function in case if no security library installed
    """
    response = await client.get("/")
    assert response.status == 200
    assert await response.text()
