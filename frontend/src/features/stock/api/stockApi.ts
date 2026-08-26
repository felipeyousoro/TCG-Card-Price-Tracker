import { http } from '../../../shared/api/http'
import type {
  BuyPayload,
  ImportPreviewRequest,
  ImportPreviewResult,
  PaginatedHoldings,
  PaginatedTransactions,
  StockQuantities,
  StockTransaction,
  TransactionCreate,
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

export async function previewImport(payload: ImportPreviewRequest) {
  const { data } = await http.post<ImportPreviewResult>('/stock/transactions/import/preview', payload)
  return data
}

export async function createTransaction(payload: TransactionCreate) {
  const { data } = await http.post<StockTransaction>('/stock/transactions', payload)
  return data
}

export async function deleteTransaction(transactionId: string) {
  await http.delete(`/stock/transactions/${transactionId}`)
}
