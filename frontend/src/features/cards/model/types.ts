export type OptcgCardListItem = {
  id: number
  card_name: string
  card_set_id: string
  card_image: string | null
}

export type PaginatedOptcgCards = {
  data: OptcgCardListItem[]
  total_count: number
  has_more: boolean
  page: number | null
  items_per_page: number | null
}

export type OptcgCardFilterOptions = {
  colors: string[]
  rarities: string[]
  set_names: string[]
}

export type OptcgCardListParams = {
  page: number
  color: string
  rarity: string
  set_name: string
}

export const OPTCG_PAGE_SIZE = 50
