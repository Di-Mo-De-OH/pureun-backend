from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_buy_now(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders", headers=headers, json={"option_id": product_1.options[0].id, "quantity": 2}
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["amount"] == 16000
    assert body["order_name"] == f"{product_1.name} {product_1.options[0].option_name} {2}개"
    assert body["thumbnail_image_key"] == f"{product_1.images[0].image_key}"


async def test_buy_now_invalid_option_id(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders", headers=headers, json={"option_id": "invalid-option_id", "quantity": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buy_now_is_active_false(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_3: Product,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders", headers=headers, json={"option_id": product_3.options[0].id, "quantity": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buy_now_over_quantity(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders", headers=headers, json={"option_id": product_1.options[0].id, "quantity": 11}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_buy_now_unauthorized(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
) -> None:

    response = await client.post("/api/v1/orders", json={"option_id": product_1.options[0].id, "quantity": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_buy_now_invalid_quantity(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders", headers=headers, json={"option_id": product_1.options[0].id, "quantity": 0}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
