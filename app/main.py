from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.products import router as products_router
from app.core.config import settings
from app.db.session import engine
from app.api.v1.orders import router as orders_router

app = FastAPI(title=settings.app_name)

app.include_router(
    orders_router,
    prefix="/api/v1",
)

app.include_router(
    products_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
    }


@app.get("/health/db")
async def database_health():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return {"database": "connected"}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
