from fastapi import status
from httpx import AsyncClient

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_cart_decrease(client: AsyncClient, product_1: Product, normal_user: User) -> None:
    option_id = product_1.options[0].id
    headers = await login(client, normal_user)
    await client.post(
        f"/api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    await client.post(
        f"/api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response = await client.post(
        f"/api/v1/cart/{option_id}/decrease",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["quantity"] == 1


async def test_cart_decrease_multiple_request(client: AsyncClient, product_1: Product, normal_user: User) -> None:
    option_id = product_1.options[0].id
    headers = await login(client, normal_user)
    await client.post(
        f"/api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response_increase = await client.post(
        f"/api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    body_increase = response_increase.json()
    assert body_increase["quantity"] == 2

    response1 = await client.post(
        f"/api/v1/cart/{option_id}/decrease",
        headers=headers,
    )
    assert response1.status_code == status.HTTP_200_OK
    body_response1 = response1.json()
    assert body_response1["quantity"] == 1

    response2 = await client.post(
        f"/api/v1/cart/{option_id}/decrease",
        headers=headers,
    )
    assert response2.status_code == status.HTTP_200_OK
    body_response2 = response2.json()
    assert body_response2["quantity"] == 1


async def test_cart_decrease_not_below_one(client: AsyncClient, product_1: Product, normal_user: User) -> None:
    option_id = product_1.options[0].id
    headers = await login(client, normal_user)
    await client.post(
        f"/api/v1/cart/{option_id}/increase",
        headers=headers,
    )
    response = await client.post(
        f"/api/v1/cart/{option_id}/decrease",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["quantity"] == 1


async def test_cart_decrease_invalid_option_id(client: AsyncClient, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/cart/invalid-option_id/decrease",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_cart_decrease_unauthorized(client: AsyncClient, product_1: Product) -> None:
    option_id = product_1.options[0].id
    response = await client.post(
        f"/api/v1/cart/{option_id}/decrease",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
