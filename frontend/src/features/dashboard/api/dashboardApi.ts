import { http } from '../../../shared/api/http'
import type {
  DashboardByItem,
  DashboardRange,
  DashboardSeries,
  DashboardSummary,
} from '../model/types'
import { DASHBOARD_BY_ITEM_LIMIT } from '../model/types'

function rangeParams(range: DashboardRange) {
  return {
    date_from: range.date_from,
    date_to: range.date_to,
  }
}

export async function getDashboardSummary(range: DashboardRange) {
  const { data } = await http.get<DashboardSummary>('/dashboard/summary', {
    params: rangeParams(range),
  })
  return data
}

export async function getDashboardSeries(range: DashboardRange) {
  const { data } = await http.get<DashboardSeries>('/dashboard/series', {
    params: rangeParams(range),
  })
  return data
}

export async function getDashboardByItem(range: DashboardRange, limit = DASHBOARD_BY_ITEM_LIMIT) {
  const { data } = await http.get<DashboardByItem>('/dashboard/by-item', {
    params: { ...rangeParams(range), limit },
  })
  return data
}
