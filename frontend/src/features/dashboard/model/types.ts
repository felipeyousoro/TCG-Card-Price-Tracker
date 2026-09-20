export type DashboardRange = {
  date_from?: string
  date_to?: string
}

export type DashboardItemType = 'card' | 'product'

export type DashboardSummary = {
  date_from: string | null
  date_to: string | null
  total_invested: number
  total_proceeds: number
  realized_pnl: number
  holdings_count: number
  remaining_cost_basis: number
}

export type DashboardSeriesPoint = {
  date: string
  buy_spend: number
  realized_pnl: number
}

export type DashboardSeries = {
  date_from: string
  date_to: string
  points: DashboardSeriesPoint[]
}

export type RankingSoldItem = {
  item_type: DashboardItemType
  card_id: number | null
  product_id: number | null
  name: string
  code: string | null
  image_url: string | null
  quantity_sold: number
  proceeds: number
  realized_gain: number
}

export type RankingHoldingItem = {
  item_type: DashboardItemType
  card_id: number | null
  product_id: number | null
  name: string
  code: string | null
  image_url: string | null
  quantity: number
  avg_unit_cost: number
  remaining_cost: number
}

export type DashboardByItem = {
  date_from: string | null
  date_to: string | null
  best_realized: RankingSoldItem[]
  worst_realized: RankingSoldItem[]
  top_holdings: RankingHoldingItem[]
}

export const ALL_TIME_RANGE: DashboardRange = {}

export const DASHBOARD_BY_ITEM_LIMIT = 10
