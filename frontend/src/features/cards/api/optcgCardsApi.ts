import { http } from '../../../shared/api/http'
import type { OptcgCardFilterOptions, OptcgCardListParams, PaginatedOptcgCards } from '../model/types'
import { OPTCG_PAGE_SIZE } from '../model/types'

export async function listOptcgCards(params: OptcgCardListParams) {
  const { data } = await http.get<PaginatedOptcgCards>('/optcg/cards', {
    params: {
      page: params.page,
      items_per_page: OPTCG_PAGE_SIZE,
      color: params.color || undefined,
      rarity: params.rarity || undefined,
      set_name: params.set_name || undefined,
    },
  })
  return data
}

export async function getOptcgCardFilters() {
  const { data } = await http.get<OptcgCardFilterOptions>('/optcg/cards/filters')
  return data
}
