from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product, ProductImage, ProductLabel, ProductOption
from app.products.schemas.create import ProductCreateRequest


async def create_product(db: AsyncSession, request: ProductCreateRequest) -> Product:
    product = Product(
        category=request.category,
        name=request.name,
        description=request.description,
        supplier_code=request.supplier_code,
    )
    db.add(product)
    try:
        await db.flush()

        for option in request.options:
            db.add(ProductOption(product_id=product.id, **option.model_dump()))

        if request.label:
            db.add(ProductLabel(product_id=product.id, **request.label.model_dump()))

        for sort_order, image_key in enumerate(request.image_keys):
            db.add(ProductImage(product_id=product.id, image_key=image_key, sort_order=sort_order))

        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="상품 등록에 실패했습니다.")
    await db.refresh(product)
    return product
