from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from tests.utils import login


async def test_create_product(client: AsyncClient, db: AsyncSession, admin_user: User) -> None:
    headers = await login(client, admin_user)

    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "category": "채소",
            "name": "산지직송 코코넛",
            "supplier_code": "늘푸른",
            "options": [{"option_name": "1kg", "price": 9000, "stock": 10}],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_product_forbidden(client: AsyncClient, db: AsyncSession, normal_user: User) -> None:
    headers = await login(client, normal_user)
    response = await client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "category": "채소",
            "name": "산지직송 코코넛",
            "supplier_code": "늘푸른",
            "options": [{"option_name": "1kg", "price": 9000, "stock": 10}],
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
