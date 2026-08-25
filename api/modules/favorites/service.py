from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth.http_exceptions import NotFoundException
from ..cards.models import Card
from ..products.models import Product
from .models import Favorite
from .schemas import FavoriteCreate, FavoriteIds, FavoriteRead


class FavoriteService:
    """Star and unstar catalog cards and products."""

    async def add(self, db: AsyncSession, user_id: int, payload: FavoriteCreate) -> FavoriteRead:
        existing = await self._find_existing(db, user_id, payload.card_id, payload.product_id)
        if existing is not None:
            return await self._to_read(db, existing)

        if payload.card_id is not None:
            card = (await db.execute(select(Card).where(Card.id == payload.card_id))).scalar_one_or_none()
            if card is None:
                raise NotFoundException(detail="Card not found")
        else:
            product = (
                await db.execute(select(Product).where(Product.id == payload.product_id))
            ).scalar_one_or_none()
            if product is None:
                raise NotFoundException(detail="Product not found")

        favorite = Favorite(user_id=user_id, card_id=payload.card_id, product_id=payload.product_id)
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return await self._to_read(db, favorite)

    async def remove(self, db: AsyncSession, user_id: int, favorite_id: UUID) -> None:
        favorite = (
            await db.execute(
                select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user_id)
            )
        ).scalar_one_or_none()
        if favorite is None:
            raise NotFoundException(detail="Favorite not found")
        await db.delete(favorite)
        await db.commit()

    async def remove_card(self, db: AsyncSession, user_id: int, card_id: int) -> None:
        favorite = await self._find_existing(db, user_id, card_id, None)
        if favorite is None:
            raise NotFoundException(detail="Favorite not found")
        await db.delete(favorite)
        await db.commit()

    async def remove_product(self, db: AsyncSession, user_id: int, product_id: int) -> None:
        favorite = await self._find_existing(db, user_id, None, product_id)
        if favorite is None:
            raise NotFoundException(detail="Favorite not found")
        await db.delete(favorite)
        await db.commit()

    async def list_ids(self, db: AsyncSession, user_id: int) -> FavoriteIds:
        rows = (await db.execute(select(Favorite).where(Favorite.user_id == user_id))).scalars().all()
        return FavoriteIds(
            card_ids=[row.card_id for row in rows if row.card_id is not None],
            product_ids=[row.product_id for row in rows if row.product_id is not None],
        )

    async def list_paginated(self, db: AsyncSession, user_id: int, skip: int, limit: int) -> dict:
        total = int(
            (
                await db.execute(select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id))
            ).scalar_one()
        )
        rows = (
            (
                await db.execute(
                    select(Favorite)
                    .where(Favorite.user_id == user_id)
                    .order_by(Favorite.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        data = [await self._to_read(db, row) for row in rows]
        return {"data": [item.model_dump(mode="json") for item in data], "total_count": total}

    async def _find_existing(
        self,
        db: AsyncSession,
        user_id: int,
        card_id: int | None,
        product_id: int | None,
    ) -> Favorite | None:
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        if card_id is not None:
            stmt = stmt.where(Favorite.card_id == card_id)
        else:
            stmt = stmt.where(Favorite.product_id == product_id)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def _to_read(self, db: AsyncSession, favorite: Favorite) -> FavoriteRead:
        if favorite.card_id is not None:
            card = (await db.execute(select(Card).where(Card.id == favorite.card_id))).scalar_one()
            return FavoriteRead(
                id=favorite.id,
                card_id=favorite.card_id,
                product_id=None,
                name=card.name,
                code=card.card_number,
                image_url=card.image_url,
                created_at=favorite.created_at,
            )
        product = (await db.execute(select(Product).where(Product.id == favorite.product_id))).scalar_one()
        return FavoriteRead(
            id=favorite.id,
            card_id=None,
            product_id=favorite.product_id,
            name=product.name,
            code=product.category,
            image_url=product.image_url,
            created_at=favorite.created_at,
        )
