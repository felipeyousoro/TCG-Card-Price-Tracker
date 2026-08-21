from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import OptcgCard
from .schemas import OptcgCardCreate

INSERT_BATCH_SIZE = 500


class OptcgCatalogService:
    """Persistence for the shared OPTCG card catalog."""

    async def bulk_insert_missing(
        self,
        cards: list[OptcgCardCreate],
        db: AsyncSession,
    ) -> tuple[int, int]:
        """Insert cards that do not already exist for the same name and set.

        Skips rows whose `(card_name, set_id)` is already in the catalog or
        duplicated within the incoming payload.

        Args:
            cards: Mapped catalog cards to consider for insert.
            db: Database session for the operation.

        Returns:
            A tuple of `(inserted, skipped)` counts.
        """
        result = await db.execute(select(OptcgCard.card_name, OptcgCard.set_id))
        existing = {(row.card_name, row.set_id) for row in result.all()}

        to_insert: list[OptcgCardCreate] = []
        skipped = 0
        seen_in_payload: set[tuple[str, str]] = set()

        for card in cards:
            key = (card.card_name, card.set_id)
            if key in existing or key in seen_in_payload:
                skipped += 1
                continue
            seen_in_payload.add(key)
            existing.add(key)
            to_insert.append(card)

        for offset in range(0, len(to_insert), INSERT_BATCH_SIZE):
            batch = to_insert[offset : offset + INSERT_BATCH_SIZE]
            db.add_all([OptcgCard(**card.model_dump()) for card in batch])
            await db.flush()

        await db.commit()
        return len(to_insert), skipped
