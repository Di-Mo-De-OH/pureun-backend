from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_delete_product(client: AsyncClient, db: AsyncSession, admin_user: User, product_1: Product) -> None:
    headers = await login(client, admin_user)

    response = await client.delete(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


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
