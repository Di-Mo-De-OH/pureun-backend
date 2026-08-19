from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product


async def test_read_all_products(
    client: AsyncClient,
    db: AsyncSession,
    product_1: Product,
    product_2: Product,
    product_3: Product,
) -> None:
    response = await client.get(
        "/api/v1/products",
    )
    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    items_by_id = {item["id"]: item for item in body["items"]}
    assert product_1.id in items_by_id
    assert product_2.id in items_by_id
    assert product_3.id not in items_by_id

    assert items_by_id[product_1.id]["discount_price"] == 8000
    assert items_by_id[product_2.id]["price"] == 15000
