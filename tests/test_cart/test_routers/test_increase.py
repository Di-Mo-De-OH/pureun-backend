from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_cart_increase(client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User) -> None:
    option_id = product_1.options[0].id
    headers = await login(client, normal_user)
    response = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["quantity"] == 1


async def test_cart_increase_multiple_request(
    client: AsyncClient, db: AsyncSession, product_1: Product, normal_user: User
) -> None:
    option_id = product_1.options[0].id
    headers = await login(client, normal_user)
    response1 = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response2 = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response3 = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    assert response1.status_code == status.HTTP_200_OK
    body = response1.json()
    assert body["quantity"] == 1
    assert response2.status_code == status.HTTP_200_OK
    body = response2.json()
    assert body["quantity"] == 2
    assert response3.status_code == status.HTTP_200_OK
    body = response3.json()
    assert body["quantity"] == 3


async def test_cart_increase_invalid_option_id(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "api/v1/cart/invalid-option_id/increase",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_cart_increase_unauthorized(client: AsyncClient, product_1: Product) -> None:
    option_id = product_1.options[0].id
    response = await client.post(
        f"api/v1/cart/{option_id}/increase",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_cart_increase_over_stock(
    client: AsyncClient, product_2: Product, db: AsyncSession, normal_user: User
) -> None:
    option_id = product_2.options[0].id
    headers = await login(client, normal_user)
    response1 = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response2 = await client.post(
        f"api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    assert response1.status_code == status.HTTP_200_OK
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
