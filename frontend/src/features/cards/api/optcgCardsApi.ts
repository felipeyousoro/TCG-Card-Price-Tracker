import { http } from '../../../shared/api/http'
import type { OptcgCardFilterOptions, OptcgCardListParams, PaginatedOptcgCards } from '../model/types'
import { OPTCG_PAGE_SIZE } from '../model/types'

export async function listOptcgCards(params: OptcgCardListParams) {
  const { data } = await http.get<PaginatedOptcgCards>('/optcg/cards', {
    params: {
      page: params.page,
      items_per_page: OPTCG_PAGE_SIZE,
      name: params.name || undefined,
      color: params.colors.length ? params.colors : undefined,
      rarity: params.rarities.length ? params.rarities : undefined,
      set_name: params.set_names.length ? params.set_names : undefined,
      base_only: params.base_only || undefined,
      sort: params.sort === 'set' ? undefined : params.sort,
    },
    paramsSerializer: { indexes: null },
  })
  return data
}

export async function getOptcgCardFilters() {
  const { data } = await http.get<OptcgCardFilterOptions>('/optcg/cards/filters')
  return data
}
