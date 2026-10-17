from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address
from app.auth.models import User
from tests.utils import create_address, login


async def test_create_address(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "일반유저",
            "phone_number": "010-1234-1234",
            "post_code": "04046",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "1층 ",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["is_default"] is True


async def test_create_address_change_is_default(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response_first = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "일반유저",
            "phone_number": "010-1234-1234",
            "post_code": "04046",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "1층 ",
        },
    )
    assert response_first.status_code == status.HTTP_201_CREATED

    response_second = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "집",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
            "is_default": True,
        },
    )
    assert response_second.status_code == status.HTTP_201_CREATED
    stmt = select(Address).where(Address.user_id == normal_user.id)
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    assert len(addresses) == 2
    first_id = response_first.json()["id"]
    second_id = response_second.json()["id"]
    default_by_id = {address.id: address.is_default for address in addresses}
    assert default_by_id[first_id] is False
    assert default_by_id[second_id] is True


async def test_create_address_over_limit(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    for _ in range(5):
        await create_address(client, headers)
    response = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "집",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
        },
    )
    stmt = select(Address).where(Address.user_id == normal_user.id)
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(addresses) == 5


async def test_create_address_unauthorized(client: AsyncClient, db: AsyncSession) -> None:
    response = await client.post(
        "/api/v1/addresses",
        json={
            "recipient_name": "집",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_address_phone_normalized(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "집",
            "phone_number": "010-1234-5678",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = await db.execute(select(Address).where(Address.id == response.json()["id"]))
    address = result.scalar_one()
    assert address.phone_number == "01012345678"


async def test_create_address_phone_invalid(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/addresses",
        headers=headers,
        json={
            "recipient_name": "집",
            "phone_number": "010123456",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
