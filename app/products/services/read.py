from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.pagination import CursorPage, CursorPageParams, paginate_by_cursor
from app.products.models import Product, ProductImage, ProductOption
from app.products.schemas.read import ProductSummaryResponse


async def get_products(db: AsyncSession, params: CursorPageParams) -> CursorPage[ProductSummaryResponse]:
    stmt = select(Product).where(Product.is_active.is_(True))
    products, next_cursor = await paginate_by_cursor(db, stmt, Product.id, params)

    if not products:
        return CursorPage(items=[], next_cursor=None)

    product_ids = [p.id for p in products]

    min_price = (
        select(
            ProductOption.product_id,
            func.min(func.coalesce(ProductOption.discount_price, ProductOption.price)).label("min_price"),
        )
        .where(ProductOption.product_id.in_(product_ids))
        .group_by(ProductOption.product_id)
        .order_by(ProductOption.product_id)
        .subquery()
    )

    option_stmt = select(ProductOption).join(
        min_price,
        (ProductOption.product_id == min_price.c.product_id)
        & (func.coalesce(ProductOption.discount_price, ProductOption.price) == min_price.c.min_price),
    )

    option_result = await db.execute(option_stmt)

    cheapest_by_product = {opt.product_id: opt for opt in option_result.scalars().all()}

    # 상품별 대표 이미지
    image_stmt = select(ProductImage).where(
        ProductImage.product_id.in_(product_ids),
        ProductImage.sort_order == 0,
    )
    image_result = await db.execute(image_stmt)
    thumbnail_by_product = {img.product_id: img for img in image_result.scalars().all()}

    items = [
        ProductSummaryResponse(
            id=product.id,
            name=product.name,
            price=cheapest_by_product[product.id].price,
            discount_price=cheapest_by_product[product.id].discount_price,
            thumbnail_image_key=thumbnail_by_product[product.id].image_key,
        )
        for product in products
    ]
    return CursorPage(items=items, next_cursor=next_cursor)
