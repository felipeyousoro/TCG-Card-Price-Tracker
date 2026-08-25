import { keepPreviousData, queryOptions, useQuery } from '@tanstack/react-query'

import { getStockQuantities, listHoldings, listTransactions } from '../api/stockApi'
import { stockKeys } from './keys'

export function holdingsQueryOptions(page: number) {
  return queryOptions({
    queryKey: stockKeys.holdings(page),
    queryFn: () => listHoldings(page),
    placeholderData: keepPreviousData,
  })
}

export function transactionsQueryOptions(page: number) {
  return queryOptions({
    queryKey: stockKeys.transactions(page),
    queryFn: () => listTransactions(page),
    placeholderData: keepPreviousData,
  })
}

export const quantitiesQueryOptions = queryOptions({
  queryKey: stockKeys.quantities(),
  queryFn: getStockQuantities,
})

export function useHoldings(page: number) {
  return useQuery(holdingsQueryOptions(page))
}

export function useTransactions(page: number) {
  return useQuery(transactionsQueryOptions(page))
}

export function useStockQuantities() {
  return useQuery(quantitiesQueryOptions)
}
