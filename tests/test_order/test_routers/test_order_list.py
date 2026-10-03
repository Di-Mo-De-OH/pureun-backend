import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.order.models import Order
from app.products.models import Product
from tests.utils import add_cart, confirm_order, login


async def test_order_list(
    client: AsyncClient, db: AsyncSession, normal_user: User, order_1: Order, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = await login(client, normal_user)

    order_response = await confirm_order(client, monkeypatch, headers, order_1)
    assert order_response == status.HTTP_200_OK

    response = await client.get(
        "api/v1/orders",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["order_id"] == order_1.id
    assert body["items"][0]["order_name"] == order_1.order_name
    assert body["items"][0]["amount"] == order_1.amount
    assert len(body["items"][0]["items"]) == 1
    assert body["items"][0]["items"][0]["option_name"] == "1kg"
    assert body["items"][0]["items"][0]["quantity"] == 2
    assert body["items"][0]["items"][0]["thumbnail_image_key"] == "products/test-thumbnail.jpg"


async def test_order_list_not_toss_confirm_order(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    order_1: Order,
) -> None:
    headers = await login(client, normal_user)
    response = await client.get(
        "api/v1/orders",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["items"] == []


async def test_order_list_excludes_other_user_order(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    normal_user2: User,
    order_1: Order,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = await login(client, normal_user)
    order_response = await confirm_order(client, monkeypatch, headers, order_1)
    assert order_response == status.HTTP_200_OK
    normal_user2_headers = await login(client, normal_user2)
    response = await client.get(
        "api/v1/orders",
        headers=normal_user2_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["items"] == []


async def test_order_list_multiple_items(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
    product_2: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 2)
    await add_cart(client, headers, product_2.options[0].id, 1)

    checkout_response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={"option_ids": [product_1.options[0].id, product_2.options[0].id]},
    )
    assert checkout_response.status_code == status.HTTP_201_CREATED
    checkout_body = checkout_response.json()

    order_stmt = select(Order).where(Order.id == checkout_body["order_id"])
    order = (await db.execute(order_stmt)).scalar_one()

    order_response = await confirm_order(client, monkeypatch, headers, order)
    assert order_response == status.HTTP_200_OK

    response = await client.get(
        "api/v1/orders",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["order_id"] == order.id

    items = body["items"][0]["items"]
    assert len(items) == 2

    items_by_option_name = {item["option_name"]: item for item in items}
    assert set(items_by_option_name.keys()) == {
        product_1.options[0].option_name,
        product_2.options[0].option_name,
    }
    assert items_by_option_name[product_1.options[0].option_name]["quantity"] == 2
    assert (
        items_by_option_name[product_1.options[0].option_name]["thumbnail_image_key"] == product_1.images[0].image_key
    )
    assert items_by_option_name[product_2.options[0].option_name]["quantity"] == 1
    assert (
        items_by_option_name[product_2.options[0].option_name]["thumbnail_image_key"] == product_2.images[0].image_key
    )
