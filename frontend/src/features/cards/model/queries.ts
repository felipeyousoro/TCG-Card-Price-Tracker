import { keepPreviousData, queryOptions, useQuery } from '@tanstack/react-query'

import { getOptcgCardFilters, listOptcgCards } from '../api/optcgCardsApi'
import { cardKeys } from './keys'
import type { OptcgCardListParams } from './types'

export const optcgCardFiltersQueryOptions = queryOptions({
  queryKey: cardKeys.filters(),
  queryFn: getOptcgCardFilters,
})

export function optcgCardListQueryOptions(params: OptcgCardListParams) {
  return queryOptions({
    queryKey: cardKeys.list(params),
    queryFn: () => listOptcgCards(params),
    placeholderData: keepPreviousData,
  })
}

export function useOptcgCardFilters() {
  return useQuery(optcgCardFiltersQueryOptions)
}

export function useOptcgCardList(params: OptcgCardListParams) {
  return useQuery(optcgCardListQueryOptions(params))
}
