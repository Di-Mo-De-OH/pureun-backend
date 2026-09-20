from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product, ProductOption
from tests.utils import add_cart, login


async def test_cart_checkout_product(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 1)

    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": [product_1.options[0].id],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["order_name"] == product_1.name
    assert body["amount"] == product_1.options[0].discount_price * 1


async def test_cart_checkout_products(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
    product_2: Product,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 2)
    await add_cart(client, headers, product_2.options[0].id, 1)

    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": [product_1.options[0].id, product_2.options[0].id],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["order_name"] in {
        f"{product_1.name} 외 1건",
        f"{product_2.name} 외 1건",
    }
    assert body["amount"] == product_1.options[0].discount_price * 2 + product_2.options[0].price * 1


async def test_cart_checkout_partial_selection(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
    product_2: Product,
) -> None:
    """장바구니에서 몇가지 옵션 선택 결제"""
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 2)
    await add_cart(client, headers, product_2.options[0].id, 1)

    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": [product_1.options[0].id],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["option_name"] == product_1.options[0].option_name
    assert body["items"][0]["quantity"] == 2
    cart_response = await client.get(
        "/api/v1/cart",
        headers=headers,
    )
    cart_body = cart_response.json()
    assert len(cart_body["items"]) == 1
    assert cart_body["items"][0]["option_name"] == product_2.options[0].option_name


async def test_cart_checkout_no_options(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 1)
    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": ["invalid-id"],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_cart_checkout_skips_ghost_item(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
    product_2: Product,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 1)
    await add_cart(client, headers, product_2.options[0].id, 1)

    await db.execute(delete(Product).where(Product.id == product_1.id))
    await db.commit()

    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={"option_ids": [product_1.options[0].id, product_2.options[0].id]},
    )
    body = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert len(body["items"]) == 1
    assert body["items"][0]["option_name"] == product_2.options[0].option_name
    assert body["items"][0]["quantity"] == 1


async def test_cart_checkout_over_stock(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
    product_1: Product,
) -> None:
    headers = await login(client, normal_user)
    await add_cart(client, headers, product_1.options[0].id, 5)
    await db.execute(update(ProductOption).where(ProductOption.id == product_1.options[0].id).values(stock=3))
    await db.commit()
    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": [product_1.options[0].id],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_cart_checkout_unauthorized(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
) -> None:
    response = await client.post(
        "/api/v1/orders/cart-checkout",
        json={"option_ids": [product_1.options[0].id]},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_cart_checkout_empty_cart(
    client: AsyncClient,
    db: AsyncSession,
    normal_user: User,
) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/orders/cart-checkout",
        headers=headers,
        json={
            "option_ids": [],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
