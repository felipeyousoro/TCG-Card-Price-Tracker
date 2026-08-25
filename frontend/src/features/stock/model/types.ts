export type ItemType = 'card' | 'product'

export type HoldingItem = {
  item_type: ItemType
  card_id: number | null
  product_id: number | null
  name: string
  code: string | null
  image_url: string | null
  quantity: number
  avg_unit_cost: number
}

export type StockLine = {
  id: string
  card_id: number | null
  product_id: number | null
  name: string
  quantity: number
  unit_price: number
  line_total: number
  notes: string | null
}

export type StockTransaction = {
  id: string
  transaction_type: 'buy' | 'sell'
  transaction_date: string
  notes: string | null
  created_at: string
  lines: StockLine[]
  total: number
}

export type StockQuantities = {
  cards: Record<string, number>
  products: Record<string, number>
}

export type BuyPayload = {
  quantity: number
  unit_price: number
  notes?: string | null
  transaction_date: string
  transaction_notes?: string | null
}

export type BuyImportRequest = {
  transaction_date: string
  notes?: string | null
  text: string
}

export type BuyImportResult = {
  fetched: number
  inserted: number
  skipped: number
  errors: { line: number; message: string }[]
  transaction_id: string | null
}

export type PaginatedHoldings = {
  data: HoldingItem[]
  total_count: number
  has_more: boolean
  page: number | null
  items_per_page: number | null
}

export type PaginatedTransactions = {
  data: StockTransaction[]
  total_count: number
  has_more: boolean
  page: number | null
  items_per_page: number | null
}

export const STOCK_PAGE_SIZE = 50
export const HISTORY_PAGE_SIZE = 20
