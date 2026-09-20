import { useMutation, useQueryClient } from '@tanstack/react-query'

import { dashboardKeys } from '../../dashboard/model/keys'
import {
  buyCard,
  buyProduct,
  createTransaction,
  deleteTransaction,
  previewImport,
  sellCard,
  sellProduct,
} from '../api/stockApi'
import { stockKeys } from './keys'
import type { BuyPayload, ImportPreviewRequest, SellPayload, TransactionCreate } from './types'

function invalidateStockAndDashboard(queryClient: ReturnType<typeof useQueryClient>) {
  return Promise.all([
    queryClient.invalidateQueries({ queryKey: stockKeys.all }),
    queryClient.invalidateQueries({ queryKey: dashboardKeys.all }),
  ])
}

export function useBuyCardMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ cardId, payload }: { cardId: number; payload: BuyPayload }) => buyCard(cardId, payload),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}

export function useBuyProductMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ productId, payload }: { productId: number; payload: BuyPayload }) =>
      buyProduct(productId, payload),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}

export function useSellCardMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ cardId, payload }: { cardId: number; payload: SellPayload }) => sellCard(cardId, payload),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}

export function useSellProductMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ productId, payload }: { productId: number; payload: SellPayload }) =>
      sellProduct(productId, payload),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}

export function usePreviewImportMutation() {
  return useMutation({
    mutationFn: (payload: ImportPreviewRequest) => previewImport(payload),
  })
}

export function useCreateTransactionMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: TransactionCreate) => createTransaction(payload),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}

export function useDeleteTransactionMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (transactionId: string) => deleteTransaction(transactionId),
    onSuccess: () => invalidateStockAndDashboard(queryClient),
  })
}
