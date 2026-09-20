"""HTTP routes for P&L dashboard aggregates."""

from datetime import date

from fastapi import APIRouter, Query

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import DashboardServiceDep
from .schemas import DashboardByItem, DashboardSeries, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Period spend, proceeds, realized P&L, and current holdings",
    responses={401: {"description": "Not authenticated"}},
)
async def get_summary(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    dashboard: DashboardServiceDep,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> DashboardSummary:
    """Cash totals are date-filtered; holdings metrics are always current."""
    return await dashboard.get_summary(db, current_user["id"], date_from, date_to)


@router.get(
    "/series",
    response_model=DashboardSeries,
    summary="Daily buy spend and realized P&L",
    responses={401: {"description": "Not authenticated"}},
)
async def get_series(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    dashboard: DashboardServiceDep,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> DashboardSeries:
    """Return one point per inclusive day, filling missing days with zeros."""
    return await dashboard.get_series(db, current_user["id"], date_from, date_to)


@router.get(
    "/by-item",
    response_model=DashboardByItem,
    summary="Best and worst realized P&L plus top holdings by remaining cost",
    responses={401: {"description": "Not authenticated"}},
)
async def get_by_item(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    dashboard: DashboardServiceDep,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
) -> DashboardByItem:
    """Rank cards and products by realized gain in range and current cost basis."""
    return await dashboard.get_by_item(db, current_user["id"], date_from, date_to, limit)
