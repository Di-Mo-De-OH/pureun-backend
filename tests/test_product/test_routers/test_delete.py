from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.order.models import Order, OrderItem
from app.products.models import Product
from tests.utils import login


async def test_delete_product(client: AsyncClient, db: AsyncSession, admin_user: User, product_1: Product) -> None:
    headers = await login(client, admin_user)

    response = await client.delete(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await db.execute(select(Product.id).where(Product.id == product_1.id))
    assert result.scalar_one_or_none() is None


async def test_delete_product_with_order_history_soft_deletes(
    client: AsyncClient, db: AsyncSession, admin_user: User, normal_user: User, product_1: Product
) -> None:
    option = product_1.options[0]
    order = Order(user_id=normal_user.id, amount=option.price, order_name=product_1.name)
    db.add(order)
    await db.flush()
    db.add(
        OrderItem(
            order_id=order.id,
            option_id=option.id,
            option_name=option.option_name,
            price=option.price,
            discount_price=option.discount_price,
            quantity=1,
        )
    )
    await db.commit()

    headers = await login(client, admin_user)
    response = await client.delete(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await db.execute(select(Product.is_active).where(Product.id == product_1.id))
    assert result.scalar_one() is False


async def test_delete_product_forbidden(
    client: AsyncClient, db: AsyncSession, normal_user: User, product_1: Product
) -> None:
    headers = await login(client, normal_user)
    response = await client.delete(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_delete_invalid_product(client: AsyncClient, db: AsyncSession, admin_user: User) -> None:
    headers = await login(client, admin_user)
    response = await client.delete(
        "/api/v1/products/invalid-product_id",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_unauthorized(client: AsyncClient, db: AsyncSession, product_1: Product) -> None:
    response = await client.delete(
        f"/api/v1/products/{product_1.id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
