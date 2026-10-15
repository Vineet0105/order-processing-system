
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductRepository:

    async def create(
        self,
        session: AsyncSession,
        data: ProductCreate,
    ) -> Product:
        product = Product(
            name=data.name,
            price=data.price,
            stock=data.stock,
        )

        session.add(product)
        await session.flush()
        await session.refresh(product)

        return product

    async def get_by_id(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> Product | None:
        return await session.get(Product, product_id)


    async def get_all(
        self,
        session: AsyncSession,   
    ) -> list[Product]:
        stmt = select(Product)
        result = await session.execute(stmt)
        return list(result.scalars().all())