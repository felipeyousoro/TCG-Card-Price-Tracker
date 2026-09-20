import type { DashboardRange } from './types'
import { DASHBOARD_BY_ITEM_LIMIT } from './types'

export const dashboardKeys = {
  all: ['dashboard'] as const,
  summary: (range: DashboardRange) => [...dashboardKeys.all, 'summary', range] as const,
  series: (range: DashboardRange) => [...dashboardKeys.all, 'series', range] as const,
  byItem: (range: DashboardRange, limit = DASHBOARD_BY_ITEM_LIMIT) =>
    [...dashboardKeys.all, 'by-item', range, limit] as const,
}
