import { useMutation, useQueryClient } from '@tanstack/react-query'

import { buyCard, buyProduct, deleteTransaction, importBuys } from '../api/stockApi'
import { stockKeys } from './keys'
import type { BuyImportRequest, BuyPayload } from './types'

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

export function useImportBuysMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: BuyImportRequest) => importBuys(payload),
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
