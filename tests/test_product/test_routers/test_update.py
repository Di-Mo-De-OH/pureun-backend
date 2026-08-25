from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.products.models import Product
from tests.utils import login


async def test_product_update(db: AsyncSession, client: AsyncClient, product_1: Product, admin_user: User) -> None:
    headers = await login(client, admin_user)
    existing_option_id = product_1.options[0].id
    existing_image_id = product_1.images[0].id

    response = await client.put(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
        json={
            "category": "수산물",
            "name": "산지직송 오징어",
            "description": "수정된 설명",
            "is_active": True,
            "supplier_code": "SUP001",
            "options": [
                {"id": existing_option_id, "option_name": "1kg", "price": 9000, "discount_price": 7000, "stock": 5},
                {"option_name": "500g", "price": 5000, "discount_price": None, "stock": 20},
            ],
            "images": [
                {"id": existing_image_id, "image_key": "products/test-thumbnail.jpg", "sort_order": 0},
            ],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물 가공식품",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
        },
    )
    assert response.status_code == status.HTTP_200_OK
    detail_response = await client.get(f"/api/v1/products/{product_1.id}")
    detail = detail_response.json()

    assert detail["name"] == "산지직송 오징어"
    assert detail["description"] == "수정된 설명"

    options_by_name = {opt["option_name"]: opt for opt in detail["options"]}
    assert len(detail["options"]) == 2
    assert options_by_name["1kg"]["price"] == 9000
    assert options_by_name["1kg"]["discount_price"] == 7000
    assert options_by_name["500g"]["price"] == 5000

    assert detail["label"]["item_name"] == "냉동 오징어"


async def test_product_update_with_out_admin_user(
    db: AsyncSession, client: AsyncClient, product_1: Product, normal_user: User
) -> None:
    headers = await login(client, normal_user)
    existing_option_id = product_1.options[0].id
    existing_image_id = product_1.images[0].id

    response = await client.put(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
        json={
            "category": "수산물",
            "name": "산지직송 오징어",
            "description": "수정된 설명",
            "is_active": True,
            "supplier_code": "SUP001",
            "options": [
                {"id": existing_option_id, "option_name": "1kg", "price": 9000, "discount_price": 7000, "stock": 5},
                {"option_name": "500g", "price": 5000, "discount_price": None, "stock": 20},
            ],
            "images": [
                {"id": existing_image_id, "image_key": "products/test-thumbnail.jpg", "sort_order": 0},
            ],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물 가공식품",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_product_update_invalid_product_id(
    db: AsyncSession, client: AsyncClient, product_1: Product, admin_user: User
) -> None:
    headers = await login(client, admin_user)
    existing_option_id = product_1.options[0].id
    existing_image_id = product_1.images[0].id

    response = await client.put(
        "/api/v1/products/invalid-product_id",
        headers=headers,
        json={
            "category": "수산물",
            "name": "산지직송 오징어",
            "description": "수정된 설명",
            "is_active": True,
            "supplier_code": "SUP001",
            "options": [
                {"id": existing_option_id, "option_name": "1kg", "price": 9000, "discount_price": 7000, "stock": 5},
                {"option_name": "500g", "price": 5000, "discount_price": None, "stock": 20},
            ],
            "images": [
                {"id": existing_image_id, "image_key": "products/test-thumbnail.jpg", "sort_order": 0},
            ],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물 가공식품",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_product_update_with_out_img(
    db: AsyncSession, client: AsyncClient, product_1: Product, admin_user: User
) -> None:
    headers = await login(client, admin_user)
    existing_option_id = product_1.options[0].id

    response = await client.put(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
        json={
            "category": "수산물",
            "name": "산지직송 오징어",
            "description": "수정된 설명",
            "is_active": True,
            "supplier_code": "SUP001",
            "options": [
                {"id": existing_option_id, "option_name": "1kg", "price": 9000, "discount_price": 7000, "stock": 5},
                {"option_name": "500g", "price": 5000, "discount_price": None, "stock": 20},
            ],
            "images": [],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물 가공식품",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_product_update_with_out_option(
    db: AsyncSession, client: AsyncClient, product_1: Product, admin_user: User
) -> None:
    headers = await login(client, admin_user)
    existing_image_id = product_1.images[0].id

    response = await client.put(
        f"/api/v1/products/{product_1.id}",
        headers=headers,
        json={
            "category": "수산물",
            "name": "산지직송 오징어",
            "description": "수정된 설명",
            "is_active": True,
            "supplier_code": "SUP001",
            "options": [],
            "images": [
                {"id": existing_image_id, "image_key": "products/test-thumbnail.jpg", "sort_order": 0},
            ],
            "label": {
                "item_name": "냉동 오징어",
                "manufacturer": "올바다수산",
                "origin": "국내산",
                "expiration_info": "제조일로부터 12개월",
                "item_group_notice": "수산물 가공식품",
                "imported_food_notice": "해당사항없음",
                "composition": "오징어 100%",
                "storage_method": "냉동보관(-18℃ 이하)",
                "safety_caution": "해동 후 재냉동 금지",
                "customer_service_phone": "1577-0000",
            },
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
