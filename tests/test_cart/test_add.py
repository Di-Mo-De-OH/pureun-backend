from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_cart_add(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    header = await login(client, normal_user)
    response = await client.post(
        "/api/v1/cart",
        headers=header,
        json={
            "option_id": product_1.options[0].id,
            "quantity": 1,
        },
    )
    body = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert body["quantity"] == 1
    assert body["option_name"] == product_1.options[0].option_name


async def test_cart_add_invalid_option_id(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    header = await login(client, normal_user)
    response = await client.post(
        "/api/v1/cart",
        headers=header,
        json={
            "option_id": "invalid-id",
            "quantity": 1,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_cart_add_unauthorized(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
) -> None:
    response = await client.post(
        "/api/v1/cart",
        json={
            "option_id": product_1.options[0].id,
            "quantity": 1,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_cart_add_under_zero_quantity(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    header = await login(client, normal_user)
    response = await client.post(
        "/api/v1/cart",
        headers=header,
        json={
            "option_id": product_1.options[0].id,
            "quantity": 0,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_cart_add_over_stock(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    normal_user: User,
) -> None:
    header = await login(client, normal_user)
    response = await client.post(
        "/api/v1/cart",
        headers=header,
        json={
            "option_id": product_1.options[0].id,
            "quantity": 11,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_cart_add_accumulates(
    client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User
) -> None:
    header = await login(client, normal_user)

    await client.post("/api/v1/cart", headers=header, json={"option_id": product_1.options[0].id, "quantity": 2})
    response = await client.post(
        "/api/v1/cart", headers=header, json={"option_id": product_1.options[0].id, "quantity": 3}
    )

    assert response.json()["quantity"] == 5


async def test_cart_add_accumulates_over_stock(
    client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User
) -> None:
    header = await login(client, normal_user)

    await client.post("/api/v1/cart", headers=header, json={"option_id": product_1.options[0].id, "quantity": 6})
    response = await client.post(
        "/api/v1/cart", headers=header, json={"option_id": product_1.options[0].id, "quantity": 6}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
