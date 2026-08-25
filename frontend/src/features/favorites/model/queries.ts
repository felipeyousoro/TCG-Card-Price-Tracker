import { keepPreviousData, queryOptions, useQuery } from '@tanstack/react-query'

import { getFavoriteIds, listFavorites } from '../api/favoritesApi'
import { favoriteKeys } from './keys'

export function favoritesListQueryOptions(page: number) {
  return queryOptions({
    queryKey: favoriteKeys.list(page),
    queryFn: () => listFavorites(page),
    placeholderData: keepPreviousData,
  })
}

export const favoriteIdsQueryOptions = queryOptions({
  queryKey: favoriteKeys.ids(),
  queryFn: getFavoriteIds,
})

export function useFavoritesList(page: number) {
  return useQuery(favoritesListQueryOptions(page))
}

export function useFavoriteIds() {
  return useQuery(favoriteIdsQueryOptions)
}
