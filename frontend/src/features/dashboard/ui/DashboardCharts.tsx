import { type ReactNode } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { formatMoney, formatSignedMoney } from '../../stock/model/format'
import { isEmptySeries } from '../model/range'
import type { DashboardSeriesPoint } from '../model/types'

const tick = { fill: '#94a3b8', fontSize: 12 }
const grid = { stroke: '#1e293b' }

function ChartCard({
  title,
  height,
  children,
}: {
  title: string
  height: number
  children: ReactNode
}) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <h2 className="mb-3 text-sm font-medium text-slate-200">{title}</h2>
      <div style={{ height }}>
        {children}
      </div>
    </article>
  )
}

export default function DashboardCharts({
  points,
  compact = false,
}: {
  points: DashboardSeriesPoint[]
  compact?: boolean
}) {
  const height = compact ? 180 : 320
  if (points.length === 0 || isEmptySeries(points)) {
    return (
      <div className={`grid gap-4 ${compact ? 'lg:grid-cols-2' : 'grid-cols-1 lg:grid-cols-2'}`}>
        <article className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="mb-2 text-sm font-medium text-slate-200">Spend over time</h2>
          <p className="text-sm text-slate-400">No buys in this range.</p>
        </article>
        <article className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="mb-2 text-sm font-medium text-slate-200">Realized P&L</h2>
          <p className="text-sm text-slate-400">No sells in this range.</p>
        </article>
      </div>
    )
  }

  return (
    <div className={`grid gap-4 ${compact ? 'lg:grid-cols-2' : 'grid-cols-1 lg:grid-cols-2'}`}>
      <ChartCard title="Spend over time" height={height}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid {...grid} />
            <XAxis dataKey="date" tick={tick} minTickGap={24} />
            <YAxis tick={tick} width={56} tickFormatter={(value: number) => formatMoney(value)} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }}
              formatter={(value) => formatMoney(Number(value ?? 0))}
            />
            <Line type="monotone" dataKey="buy_spend" name="Buy spend" stroke="#fbbf24" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="Realized P&L" height={height}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid {...grid} />
            <XAxis dataKey="date" tick={tick} minTickGap={24} />
            <YAxis tick={tick} width={56} tickFormatter={(value: number) => formatSignedMoney(value)} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }}
              formatter={(value) => formatSignedMoney(Number(value ?? 0))}
            />
            <Line type="monotone" dataKey="realized_pnl" name="Realized P&L" stroke="#34d399" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  )
}
