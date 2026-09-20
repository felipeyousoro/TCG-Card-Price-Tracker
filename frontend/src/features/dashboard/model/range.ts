import { todayISODate } from '../../stock/model/format'
import type { DashboardRange } from './types'

export type DatePreset = '30' | '90' | 'year' | 'all' | 'custom'

function pad(value: number) {
  return String(value).padStart(2, '0')
}

function toISODate(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function daysAgoInclusive(days: number) {
  const [year, month, day] = todayISODate().split('-').map(Number)
  const date = new Date(year, month - 1, day)
  date.setDate(date.getDate() - (days - 1))
  return toISODate(date)
}

export function startOfYearISO() {
  return `${new Date().getFullYear()}-01-01`
}

export function rangeForPreset(preset: Exclude<DatePreset, 'custom'>): DashboardRange {
  if (preset === 'all') return {}
  if (preset === 'year') return { date_from: startOfYearISO(), date_to: todayISODate() }
  const days = preset === '30' ? 30 : 90
  return { date_from: daysAgoInclusive(days), date_to: todayISODate() }
}

export function isEmptySeries(points: { buy_spend: number; realized_pnl: number }[]) {
  return points.every((point) => point.buy_spend === 0 && point.realized_pnl === 0)
}
