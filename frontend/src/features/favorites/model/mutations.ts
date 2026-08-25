import { useMutation, useQueryClient } from '@tanstack/react-query'

import { addFavorite, removeCardFavorite, removeProductFavorite } from '../api/favoritesApi'
import { favoriteKeys } from './keys'
import type { FavoriteIds } from './types'

export function useToggleCardFavorite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ cardId, isFavorite }: { cardId: number; isFavorite: boolean }) => {
      if (isFavorite) {
        await removeCardFavorite(cardId)
      } else {
        await addFavorite({ card_id: cardId })
      }
    },
    onMutate: async ({ cardId, isFavorite }) => {
      await queryClient.cancelQueries({ queryKey: favoriteKeys.ids() })
      const previous = queryClient.getQueryData<FavoriteIds>(favoriteKeys.ids())
      queryClient.setQueryData<FavoriteIds>(favoriteKeys.ids(), (current) => {
        const ids = current ?? { card_ids: [], product_ids: [] }
        return {
          ...ids,
          card_ids: isFavorite ? ids.card_ids.filter((id) => id !== cardId) : [...ids.card_ids, cardId],
        }
      })
      return { previous }
    },
    onError: (_error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(favoriteKeys.ids(), context.previous)
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: favoriteKeys.all })
    },
  })
}

export function useToggleProductFavorite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ productId, isFavorite }: { productId: number; isFavorite: boolean }) => {
      if (isFavorite) {
        await removeProductFavorite(productId)
      } else {
        await addFavorite({ product_id: productId })
      }
    },
    onMutate: async ({ productId, isFavorite }) => {
      await queryClient.cancelQueries({ queryKey: favoriteKeys.ids() })
      const previous = queryClient.getQueryData<FavoriteIds>(favoriteKeys.ids())
      queryClient.setQueryData<FavoriteIds>(favoriteKeys.ids(), (current) => {
        const ids = current ?? { card_ids: [], product_ids: [] }
        return {
          ...ids,
          product_ids: isFavorite
            ? ids.product_ids.filter((id) => id !== productId)
            : [...ids.product_ids, productId],
        }
      })
      return { previous }
    },
    onError: (_error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(favoriteKeys.ids(), context.previous)
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: favoriteKeys.all })
    },
  })
}
