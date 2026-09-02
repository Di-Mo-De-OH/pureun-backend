from fastapi import status
from httpx import AsyncClient

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_cart_delete(client: AsyncClient, normal_user: User, product_1: Product) -> None:
    headers = await login(client, normal_user)
    response = await client.delete(f"/api/v1/cart/{product_1.options[0].id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_cart_delete_invalid_option(client: AsyncClient,normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.delete("/api/v1/cart/invalid-option_id", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_cart_delete_unauthorized(client: AsyncClient, product_1: Product) -> None:
    response = await client.delete(
        f"/api/v1/cart/{product_1.options[0].id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
