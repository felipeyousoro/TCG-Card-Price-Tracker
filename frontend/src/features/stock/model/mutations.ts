import { useMutation, useQueryClient } from '@tanstack/react-query'

import { buyCard, buyProduct, createTransaction, deleteTransaction, previewImport } from '../api/stockApi'
import { stockKeys } from './keys'
import type { BuyPayload, ImportPreviewRequest, TransactionCreate } from './types'

function invalidateStock(queryClient: ReturnType<typeof useQueryClient>) {
  return queryClient.invalidateQueries({ queryKey: stockKeys.all })
}

export function useBuyCardMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ cardId, payload }: { cardId: number; payload: BuyPayload }) => buyCard(cardId, payload),
    onSuccess: () => invalidateStock(queryClient),
  })
}

export function useBuyProductMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ productId, payload }: { productId: number; payload: BuyPayload }) =>
      buyProduct(productId, payload),
    onSuccess: () => invalidateStock(queryClient),
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
    onSuccess: () => invalidateStock(queryClient),
  })
}

export function useDeleteTransactionMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (transactionId: string) => deleteTransaction(transactionId),
    onSuccess: () => invalidateStock(queryClient),
  })
}
