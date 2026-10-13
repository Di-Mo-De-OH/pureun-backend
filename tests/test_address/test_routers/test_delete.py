from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address
from app.auth.models import User
from tests.utils import create_address, login


async def test_delete_address(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.delete(
        f"/api/v1/addresses/{address['id']}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    stmt = select(Address).where(Address.id == address["id"])
    result = await db.execute(stmt)
    address_in_db = result.scalar_one_or_none()
    assert address_in_db is None


async def test_delete_address_next_is_default(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    first_address = await create_address(client, headers)
    second_address = await create_address(client, headers)
    response = await client.delete(
        f"/api/v1/addresses/{first_address['id']}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    address_response = await client.get(
        "/api/v1/addresses",
        headers=headers,
    )
    body = address_response.json()
    assert len(body) == 1
    assert body[0]["id"] == second_address["id"]
    assert body[0]["is_default"] is True


async def test_delete_address_last_one(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.delete(
        f"/api/v1/addresses/{address['id']}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    address_response = await client.get(
        "/api/v1/addresses",
        headers=headers,
    )
    body = address_response.json()
    assert len(body) == 0
    assert body == []


async def test_delete_address_other_user(
    client: AsyncClient, db: AsyncSession, normal_user: User, normal_user2: User
) -> None:
    normal_user_headers = await login(client, normal_user)
    normal_user2_headers = await login(client, normal_user2)
    address = await create_address(client, normal_user_headers)
    response = await client.delete(
        f"/api/v1/addresses/{address['id']}",
        headers=normal_user2_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    address_response = await client.get(
        "/api/v1/addresses",
        headers=normal_user_headers,
    )
    body = address_response.json()
    assert len(body) == 1
    assert body[0]["id"] == address["id"]


async def test_delete_address_not_found(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.delete(
        "/api/v1/addresses/invalid-address-id",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_address_unauthorized(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.delete(f"/api/v1/addresses/{address['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
