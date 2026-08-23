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
            "image_keys": ["products/01M07YY54WWGFSBDS9P8XQX2E5.jpeg"],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
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
            "image_keys": ["products/01M07YY54WWGFSBDS9P8XQX2E5.jpeg"],
            "label": {
                "label": {
                    "item_name": "냉동 오징어",
                    "manufacturer": "올바다수산",
                    "origin": "국내산",
                    "expiration_info": "제조일로부터 12개월",
                    "item_group_notice": "수산물",
                    "imported_food_notice": "해당사항없음",
                    "composition": "오징어 100%",
                    "storage_method": "냉동보관(-18℃ 이하)",
                    "safety_caution": "해동 후 재냉동 금지",
                    "customer_service_phone": "1577-0000",
                }
            },
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
