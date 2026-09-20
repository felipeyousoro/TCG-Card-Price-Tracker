export type OptcgCardListItem = {
  id: number
  card_name: string
  card_set_id: string
  rarity: string
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

export type OptcgCardSort = 'set' | 'number' | 'number_desc'

export type OptcgCardListParams = {
  page: number
  name: string
  colors: string[]
  rarities: string[]
  set_names: string[]
  base_only: boolean
  sort: OptcgCardSort
}

export const OPTCG_PAGE_SIZE = 50

export const OPTCG_SORT_CYCLE: OptcgCardSort[] = ['set', 'number', 'number_desc']

export const OPTCG_SORT_LABEL: Record<OptcgCardSort, string> = {
  set: 'Sort: set',
  number: 'Sort: number ↑',
  number_desc: 'Sort: number ↓',
}

export function nextOptcgSort(current: OptcgCardSort): OptcgCardSort {
  const index = OPTCG_SORT_CYCLE.indexOf(current)
  return OPTCG_SORT_CYCLE[(index + 1) % OPTCG_SORT_CYCLE.length]
}
