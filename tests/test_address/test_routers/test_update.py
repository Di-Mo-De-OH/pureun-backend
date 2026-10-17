from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from tests.utils import create_address, login


async def test_update_address(
    client: AsyncClient,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.put(
        f"/api/v1/addresses/{address['id']}",
        headers=headers,
        json={
            "recipient_name": "updated_name",
            "phone_number": "010-1111-1111",
            "post_code": "00000",
            "base_address": "updated_base_address",
            "detail_address": "updated_detail_address",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["id"] == address["id"]

    address_response = await client.get("/api/v1/addresses", headers=headers)
    body = address_response.json()
    assert body[0]["recipient_name"] == "updated_name"
    assert body[0]["phone_number"] == "010-1111-1111"
    assert body[0]["post_code"] == "00000"
    assert body[0]["base_address"] == "updated_base_address"
    assert body[0]["detail_address"] == "updated_detail_address"


async def test_update_address_change_is_default(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    address_1 = await create_address(client, headers)
    address_2 = await create_address(client, headers)

    response = await client.put(
        f"/api/v1/addresses/{address_2['id']}",
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

    assert response.status_code == status.HTTP_200_OK

    addresses = await client.get(
        "/api/v1/addresses",
        headers=headers,
    )
    body = addresses.json()
    by_id = {item["id"]: item for item in body}

    assert len(body) == 2
    assert by_id[address_2["id"]]["is_default"] is True
    assert by_id[address_1["id"]]["is_default"] is False


async def test_update_address_keep_default(
    client: AsyncClient,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.put(
        f"/api/v1/addresses/{address['id']}",
        headers=headers,
        json={
            "recipient_name": "changed",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
            "is_default": False,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    get_address = await client.get(
        "/api/v1/addresses",
        headers=headers,
    )
    body = get_address.json()
    assert body[0]["is_default"] is True
    assert body[0]["recipient_name"] == "changed"


async def test_update_address_other_user(
    client: AsyncClient,
    normal_user: User,
    normal_user2: User,
) -> None:
    headers_user_1 = await login(client, normal_user)
    headers_user_2 = await login(client, normal_user2)
    address = await create_address(client, headers_user_1)
    response = await client.put(
        f"/api/v1/addresses/{address['id']}",
        headers=headers_user_2,
        json={
            "recipient_name": "home",
            "phone_number": "010-1111-1111",
            "post_code": "00000",
            "base_address": "home_base_address",
            "detail_address": "home_detail_address",
            "is_default": False,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    get_address = await client.get(
        "/api/v1/addresses",
        headers=headers_user_1,
    )
    body = get_address.json()
    assert body[0]["recipient_name"] == "집"
    assert body[0]["phone_number"] == "010-1234-1234"
    assert body[0]["post_code"] == "04044"
    assert body[0]["base_address"] == "서울특별시 마포구 ..."
    assert body[0]["detail_address"] == "2층"
    assert body[0]["is_default"] is True


async def test_update_address_invalid_id(
    client: AsyncClient,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.put(
        "/api/v1/addresses/invalid-id",
        headers=headers,
        json={
            "recipient_name": "updated",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "updated",
            "detail_address": "updated ",
            "is_default": True,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_address_unauthorized(
    client: AsyncClient,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.put(
        f"/api/v1/addresses/{address['id']}",
        json={
            "recipient_name": "updated",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "updated",
            "detail_address": "updated ",
            "is_default": False,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
