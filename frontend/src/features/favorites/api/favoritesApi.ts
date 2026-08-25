import { http } from '../../../shared/api/http'
import type { FavoriteIds, FavoriteRead, PaginatedFavorites } from '../model/types'
import { FAVORITES_PAGE_SIZE } from '../model/types'

export async function listFavorites(page: number) {
  const { data } = await http.get<PaginatedFavorites>('/favorites', {
    params: { page, items_per_page: FAVORITES_PAGE_SIZE },
  })
  return data
}

export async function getFavoriteIds() {
  const { data } = await http.get<FavoriteIds>('/favorites/ids')
  return data
}

export async function addFavorite(payload: { card_id?: number; product_id?: number }) {
  const { data } = await http.post<FavoriteRead>('/favorites', payload)
  return data
}

export async function removeCardFavorite(cardId: number) {
  await http.delete(`/favorites/cards/${cardId}`)
}

export async function removeProductFavorite(productId: number) {
  await http.delete(`/favorites/products/${productId}`)
}
