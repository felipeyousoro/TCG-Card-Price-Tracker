import { keepPreviousData, queryOptions, useQuery } from '@tanstack/react-query'

import { getDashboardByItem, getDashboardSeries, getDashboardSummary } from '../api/dashboardApi'
import { dashboardKeys } from './keys'
import { DASHBOARD_BY_ITEM_LIMIT, type DashboardRange } from './types'

export function dashboardSummaryQueryOptions(range: DashboardRange) {
  return queryOptions({
    queryKey: dashboardKeys.summary(range),
    queryFn: () => getDashboardSummary(range),
    placeholderData: keepPreviousData,
  })
}

export function dashboardSeriesQueryOptions(range: DashboardRange) {
  return queryOptions({
    queryKey: dashboardKeys.series(range),
    queryFn: () => getDashboardSeries(range),
    placeholderData: keepPreviousData,
  })
}

export function dashboardByItemQueryOptions(range: DashboardRange, limit = DASHBOARD_BY_ITEM_LIMIT) {
  return queryOptions({
    queryKey: dashboardKeys.byItem(range, limit),
    queryFn: () => getDashboardByItem(range, limit),
    placeholderData: keepPreviousData,
  })
}

export function useDashboardSummary(range: DashboardRange) {
  return useQuery(dashboardSummaryQueryOptions(range))
}

export function useDashboardSeries(range: DashboardRange) {
  return useQuery(dashboardSeriesQueryOptions(range))
}

export function useDashboardByItem(range: DashboardRange, limit = DASHBOARD_BY_ITEM_LIMIT) {
  return useQuery(dashboardByItemQueryOptions(range, limit))
}
