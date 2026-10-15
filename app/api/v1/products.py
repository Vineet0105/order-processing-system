from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

service = ProductService()


@router.post(
    "/CreateProduct",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_db),
):
    return await service.create_product(session, data)


@router.get(
    "GetProductByID/{product_id}",
    response_model=ProductResponse,
)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
):
    product = await service.get_product(session, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.get(
        "/get_all_products",
    response_model = list[ProductResponse]
)
async def get_all_products(
    session:AsyncSession=Depends(get_db)
):
    products = await service.get_all_products(session)
    return products
