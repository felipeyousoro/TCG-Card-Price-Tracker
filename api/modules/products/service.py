from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth.http_exceptions import NotFoundException
from .crud import crud_products
from .models import Product
from .schemas import ProductCreate, ProductListItem, ProductRead


class ProductCatalogService:
    """Persistence for the shared product catalog."""

    async def list_paginated(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        q: str | None = None,
    ) -> dict:
        """Return a page of products, optionally filtered by name."""
        if not q or not q.strip():
            return await crud_products.get_multi(
                db=db,
                offset=skip,
                limit=limit,
                schema_to_select=ProductListItem,
                sort_columns=["name"],
                sort_orders=["asc"],
            )

        pattern = _ilike_pattern(q.strip())
        total = int(
            (
                await db.execute(
                    select(func.count()).select_from(Product).where(Product.name.ilike(pattern, escape="\\"))
                )
            ).scalar_one()
        )

        stmt = (
            select(Product)
            .where(Product.name.ilike(pattern, escape="\\"))
            .order_by(Product.name.asc())
            .offset(skip)
            .limit(limit)
        )
        rows = (await db.execute(stmt)).scalars().all()
        return {
            "data": [ProductListItem.model_validate(row).model_dump(mode="json") for row in rows],
            "total_count": total,
        }

    async def get_by_id(self, db: AsyncSession, product_id: int) -> ProductRead:
        """Return one catalog product or raise if it does not exist."""
        product = await crud_products.get(db=db, id=product_id, schema_to_select=ProductRead)
        if not product:
            raise NotFoundException(detail="Product not found")
        return product

    async def create(
        self,
        db: AsyncSession,
        payload: ProductCreate,
        user_id: int,
        *,
        commit: bool = True,
    ) -> ProductRead:
        """Insert a shared catalog product attributed to the creating user."""
        product = Product(
            name=payload.name.strip(),
            category=payload.category.value,
            set_name=payload.set_name.strip() if payload.set_name else None,
            image_url=payload.image_url.strip() if payload.image_url else None,
            created_by_user_id=user_id,
        )
        db.add(product)
        if commit:
            await db.commit()
            await db.refresh(product)
        else:
            await db.flush()
        return ProductRead.model_validate(product)

    async def find_by_name_ilike(self, db: AsyncSession, name: str) -> list[Product]:
        """Case-insensitive exact name match (ILIKE without wildcards)."""
        stmt = select(Product).where(Product.name.ilike(name, escape="\\"))
        return list((await db.execute(stmt)).scalars().all())


def _ilike_pattern(q: str) -> str:
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"
