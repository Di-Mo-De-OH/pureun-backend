from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from tests.utils import create_address, login


async def test_read_addresses(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:

    headers = await login(client, normal_user)
    for _ in range(2):
        await create_address(client, headers)
    await create_address(client, headers, True)
    response = await client.get("/api/v1/addresses", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 3
    assert body[0]["is_default"] is True
    assert body[0]["phone_number"] == "010-1234-1234"


async def test_read_addresses_try_search_other_user(
    client: AsyncClient, db: AsyncSession, normal_user: User, normal_user2: User
) -> None:
    headers = await login(client, normal_user)
    for _ in range(3):
        await create_address(client, headers)
    headers_normal_user2 = await login(client, normal_user2)
    response = await client.get(
        "/api/v1/addresses",
        headers=headers_normal_user2,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body == []


async def test_read_addresses_unauthorized(client: AsyncClient, db: AsyncSession) -> None:
    response = await client.get(
        "/api/v1/addresses",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
