from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from ..stock.enums import ItemType


class DashboardSummary(BaseModel):
    """Period cash metrics plus current holdings snapshot."""

    model_config = ConfigDict(extra="forbid")

    date_from: date | None = None
    date_to: date | None = None
    total_invested: float
    total_proceeds: float
    realized_pnl: float
    holdings_count: int
    remaining_cost_basis: float


class DashboardSeriesPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    buy_spend: float
    realized_pnl: float


class DashboardSeries(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_from: date
    date_to: date
    points: list[DashboardSeriesPoint] = Field(default_factory=list)


class DashboardItemGain(BaseModel):
    """Realized P&L for one catalog item inside the date range."""

    model_config = ConfigDict(extra="forbid")

    item_type: ItemType
    card_id: int | None = None
    product_id: int | None = None
    name: str
    code: str | None = None
    image_url: str | None = None
    quantity_sold: int
    proceeds: float
    realized_gain: float


class DashboardHoldingRank(BaseModel):
    """Current holding ranked by remaining cost basis."""

    model_config = ConfigDict(extra="forbid")

    item_type: ItemType
    card_id: int | None = None
    product_id: int | None = None
    name: str
    code: str | None = None
    image_url: str | None = None
    quantity: int
    avg_unit_cost: float
    remaining_cost: float


class DashboardByItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_from: date | None = None
    date_to: date | None = None
    best_realized: list[DashboardItemGain] = Field(default_factory=list)
    worst_realized: list[DashboardItemGain] = Field(default_factory=list)
    top_holdings: list[DashboardHoldingRank] = Field(default_factory=list)
