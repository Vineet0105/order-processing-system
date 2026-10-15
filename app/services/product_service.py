
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:

    def __init__(self):
        self.repository = ProductRepository()

    async def create_product(
        self,
        session: AsyncSession,
        data: ProductCreate,
    ):
        async with session.begin():
            product = await self.repository.create(
                session,
                data,
            )

        return product

    async def get_product(
        self,
        session: AsyncSession,
        product_id: int,
    ):
        return await self.repository.get_by_id(
            session,
            product_id,
        )


    async def get_all_products(
            self,
            session:AsyncSession
    ):
        return await self.repository.get_all(session)