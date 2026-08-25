export type FavoriteRead = {
  id: string
  card_id: number | null
  product_id: number | null
  name: string
  code: string | null
  image_url: string | null
  created_at: string
}

export type FavoriteIds = {
  card_ids: number[]
  product_ids: number[]
}

export type PaginatedFavorites = {
  data: FavoriteRead[]
  total_count: number
  has_more: boolean
  page: number | null
  items_per_page: number | null
}

export const FAVORITES_PAGE_SIZE = 50
