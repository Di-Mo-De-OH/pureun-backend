from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.order.models import OrderItem
from app.products.models import Product, ProductOption


async def delete_product(db: AsyncSession, product_id: str) -> None:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    order_item_stmt = (
        select(OrderItem.id)
        .join(ProductOption, OrderItem.option_id == ProductOption.id)
        .where(ProductOption.product_id == product_id)
        .limit(1)
    )
    order_item_result = await db.execute(order_item_stmt)
    order_item = order_item_result.scalar_one_or_none()

    if order_item is None:
        await db.delete(product)
    else:
        product.is_active = False
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        await db.execute(update(Product).where(Product.id == product_id).values(is_active=False))
        await db.commit()
