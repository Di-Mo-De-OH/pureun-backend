from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.order.models import Order
from app.products.models import Product
from tests.utils import assert_delivery_snapshot, create_address, login


async def test_buy_now(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": product_1.options[0].id, "quantity": 2, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["amount"] == 16000
    assert body["order_name"] == f"{product_1.name} {product_1.options[0].option_name} {2}개"
    assert body["thumbnail_image_key"] == f"{product_1.images[0].image_key}"
    await assert_delivery_snapshot(db, body["order_id"])


async def test_buy_now_invalid_option_id(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": "invalid-option_id", "quantity": 1, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buy_now_is_active_false(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_3: Product,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": product_3.options[0].id, "quantity": 1, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buy_now_over_quantity(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": product_1.options[0].id, "quantity": 11, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_buy_now_unauthorized(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
) -> None:

    response = await client.post(
        "/api/v1/orders",
        json={"option_id": product_1.options[0].id, "quantity": 1, "address_id": "address-id"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_buy_now_invalid_quantity(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": product_1.options[0].id, "quantity": 0, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_buy_now_address_snapshot(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    address = await create_address(client, headers)
    response = await client.post(
        "/api/v1/orders",
        headers=headers,
        json={"option_id": product_1.options[0].id, "quantity": 2, "address_id": address["id"]},
    )
    assert response.status_code == status.HTTP_201_CREATED
    updated_address = await client.put(
        f"/api/v1/addresses/{address['id']}",
        headers=headers,
        json={
            "recipient_name": "updated",
            "phone_number": "010-1234-1234",
            "post_code": "04044",
            "base_address": "서울특별시 마포구 ...",
            "detail_address": "2층 ",
        },
    )
    assert updated_address.status_code == status.HTTP_200_OK
    body = response.json()
    await assert_delivery_snapshot(db, body["order_id"])


async def test_buy_now_other_user_address(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
    normal_user2: User,
) -> None:
    headers_normal_user = await login(client, normal_user)
    headers_normal_user2 = await login(client, normal_user2)
    normal_user2_address = await create_address(client, headers_normal_user2)
    response = await client.post(
        "/api/v1/orders",
        headers=headers_normal_user,
        json={"option_id": product_1.options[0].id, "quantity": 2, "address_id": normal_user2_address["id"]},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    stmt = select(Order).where(Order.user_id == normal_user.id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    assert order is None
