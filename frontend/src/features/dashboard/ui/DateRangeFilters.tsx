import { todayISODate } from '../../stock/model/format'
import { rangeForPreset, type DatePreset } from '../model/range'
import type { DashboardRange } from '../model/types'

const presetClass = (active: boolean) =>
  active
    ? 'rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 text-sm text-amber-200'
    : 'rounded-lg border border-slate-800 px-3 py-1.5 text-sm text-slate-400 hover:text-slate-200'

const PRESETS: { id: Exclude<DatePreset, 'custom'>; label: string }[] = [
  { id: '30', label: '30 days' },
  { id: '90', label: '90 days' },
  { id: 'year', label: 'Year' },
  { id: 'all', label: 'All time' },
]

export default function DateRangeFilters({
  preset,
  customFrom,
  customTo,
  onPreset,
  onCustomChange,
}: {
  preset: DatePreset
  customFrom: string
  customTo: string
  onPreset: (preset: Exclude<DatePreset, 'custom'>) => void
  onCustomChange: (range: { date_from: string; date_to: string }) => void
}) {
  return (
    <div className="mb-6 flex flex-col gap-3">
      <div className="flex flex-wrap gap-2">
        {PRESETS.map((item) => (
          <button key={item.id} type="button" className={presetClass(preset === item.id)} onClick={() => onPreset(item.id)}>
            {item.label}
          </button>
        ))}
        <button type="button" className={presetClass(preset === 'custom')} onClick={() => onCustomChange({
          date_from: customFrom || rangeForPreset('30').date_from || todayISODate(),
          date_to: customTo || todayISODate(),
        })}>
          Custom
        </button>
      </div>
      {preset === 'custom' ? (
        <div className="flex flex-wrap gap-3">
          <label className="text-sm">
            <span className="mb-1.5 block text-slate-400">From</span>
            <input
              type="date"
              value={customFrom}
              onChange={(event) => onCustomChange({ date_from: event.target.value, date_to: customTo })}
              className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-amber-500/60"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1.5 block text-slate-400">To</span>
            <input
              type="date"
              value={customTo}
              onChange={(event) => onCustomChange({ date_from: customFrom, date_to: event.target.value })}
              className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-amber-500/60"
            />
          </label>
        </div>
      ) : null}
    </div>
  )
}

export function activeRange(preset: DatePreset, customFrom: string, customTo: string): DashboardRange {
  if (preset === 'custom') {
    return {
      date_from: customFrom || undefined,
      date_to: customTo || undefined,
    }
  }
  return rangeForPreset(preset)
}
