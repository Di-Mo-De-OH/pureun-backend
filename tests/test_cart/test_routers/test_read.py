from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product, ProductOption
from tests.utils import login


async def test_cart_read_empty(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    header = await login(client, normal_user)
    response = await client.get("/api/v1/cart", headers=header)
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["items"] == []
    assert body["total_price"] == 0


async def test_cart_read(client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User) -> None:
    header = await login(client, normal_user)
    option = product_1.options[0]
    await client.post("/api/v1/cart", headers=header, json={"option_id": option.id, "quantity": 2})

    response = await client.get("/api/v1/cart", headers=header)
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(body["items"]) == 1

    item = body["items"][0]
    assert item["option_id"] == option.id
    assert item["option_name"] == option.option_name
    assert item["quantity"] == 2
    assert item["price"] == option.price
    assert item["discount_price"] == option.discount_price
    assert item["total_option_price"] == option.discount_price * 2
    assert item["thumbnail_image_key"] == product_1.images[0].image_key
    assert body["total_price"] == option.discount_price * 2


async def test_cart_read_uses_price_when_no_discount(
    client: AsyncClient, db: AsyncSession, product_2: Product, normal_user: User
) -> None:
    header = await login(client, normal_user)
    result = await db.execute(select(ProductOption).where(ProductOption.product_id == product_2.id))
    option = result.scalar_one()

    await client.post("/api/v1/cart", headers=header, json={"option_id": option.id, "quantity": 1})

    response = await client.get("/api/v1/cart", headers=header)
    body = response.json()

    assert body["items"][0]["total_option_price"] == option.price
    assert body["total_price"] == option.price


async def test_cart_read_multiple_items(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    product_2: Product,
    normal_user: User,
) -> None:
    header = await login(client, normal_user)
    result = await db.execute(select(ProductOption).where(ProductOption.product_id == product_2.id))
    option_2 = result.scalar_one()

    await client.post("/api/v1/cart", headers=header, json={"option_id": product_1.options[0].id, "quantity": 2})
    await client.post("/api/v1/cart", headers=header, json={"option_id": option_2.id, "quantity": 1})

    response = await client.get("/api/v1/cart", headers=header)
    body = response.json()

    expected_total = product_1.options[0].discount_price * 2 + option_2.price
    assert response.status_code == status.HTTP_200_OK
    assert len(body["items"]) == 2
    assert body["total_price"] == expected_total


async def test_cart_read_skips_ghost_item(
    client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User
) -> None:
    header = await login(client, normal_user)
    option_id = product_1.options[0].id
    await client.post("/api/v1/cart", headers=header, json={"option_id": option_id, "quantity": 1})

    await db.execute(delete(Product).where(Product.id == product_1.id))
    await db.commit()

    response = await client.get("/api/v1/cart", headers=header)
    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body["items"] == []
    assert body["total_price"] == 0


async def test_cart_read_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/cart")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
