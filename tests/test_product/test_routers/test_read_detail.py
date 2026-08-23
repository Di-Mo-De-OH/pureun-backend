from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product


async def test_product_detail(
    db: AsyncSession,
    product_1: Product,
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/api/v1/products/{product_1.id}",
    )
    body = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert body["id"] == product_1.id
    assert len(body["options"]) == 1
    assert body["options"][0]["option_name"] == "1kg"
    assert len(body["images"]) == 1
    assert body["images"][0]["image_key"] == "products/test-thumbnail.jpg"
    assert body["label"]["item_name"] == "냉동 오징어"


async def test_product_detail_not_found(
    db: AsyncSession,
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/products/invalid_id",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_product_detail_is_active_false(
    client: AsyncClient,
    db: AsyncSession,
    product_3: Product,
) -> None:
    response = await client.get(
        f"/api/v1/products/{product_3.id}",
    )
    body = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert body["id"] == product_3.id
    assert body["is_active"] is False
