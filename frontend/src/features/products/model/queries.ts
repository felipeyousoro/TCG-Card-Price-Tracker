import { keepPreviousData, queryOptions, useQuery } from '@tanstack/react-query'

import { searchProducts } from '../api/productsApi'
import { productKeys } from './keys'

export function productSearchQueryOptions(q: string) {
  return queryOptions({
    queryKey: productKeys.list(q),
    queryFn: () => searchProducts(q),
    enabled: q.trim().length > 0,
    placeholderData: keepPreviousData,
  })
}

export function useProductSearch(q: string) {
  return useQuery(productSearchQueryOptions(q))
}
