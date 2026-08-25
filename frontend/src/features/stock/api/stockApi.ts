import { http } from '../../../shared/api/http'
import type {
  BuyImportRequest,
  BuyImportResult,
  BuyPayload,
  PaginatedHoldings,
  PaginatedTransactions,
  StockQuantities,
  StockTransaction,
} from '../model/types'
import { HISTORY_PAGE_SIZE, STOCK_PAGE_SIZE } from '../model/types'

export async function listHoldings(page: number) {
  const { data } = await http.get<PaginatedHoldings>('/stock', {
    params: { page, items_per_page: STOCK_PAGE_SIZE },
  })
  return data
}

export async function listTransactions(page: number) {
  const { data } = await http.get<PaginatedTransactions>('/stock/transactions', {
    params: { page, items_per_page: HISTORY_PAGE_SIZE },
  })
  return data
}

export async function getStockQuantities() {
  const { data } = await http.get<StockQuantities>('/stock/quantities')
  return data
}

export async function buyCard(cardId: number, payload: BuyPayload) {
  const { data } = await http.post<StockTransaction>(`/stock/cards/${cardId}/buy`, payload)
  return data
}

export async function buyProduct(productId: number, payload: BuyPayload) {
  const { data } = await http.post<StockTransaction>(`/stock/products/${productId}/buy`, payload)
  return data
}

export async function importBuys(payload: BuyImportRequest) {
  const { data } = await http.post<BuyImportResult>('/stock/transactions/import', payload)
  return data
}

export async function deleteTransaction(transactionId: string) {
  await http.delete(`/stock/transactions/${transactionId}`)
}
