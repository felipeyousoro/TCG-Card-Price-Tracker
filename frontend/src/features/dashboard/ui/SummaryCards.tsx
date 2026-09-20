import { formatMoney, formatSignedMoney } from '../../stock/model/format'
import type { DashboardSummary } from '../model/types'

function pnlClass(value: number) {
  if (value > 0) return 'text-emerald-400'
  if (value < 0) return 'text-red-300'
  return 'text-slate-100'
}

export default function SummaryCards({
  summary,
  compact = false,
}: {
  summary: DashboardSummary
  compact?: boolean
}) {
  const cards = [
    { label: 'Total invested', value: formatMoney(summary.total_invested) },
    { label: 'Total proceeds', value: formatMoney(summary.total_proceeds) },
    { label: 'Realized P&L', value: formatSignedMoney(summary.realized_pnl), className: pnlClass(summary.realized_pnl) },
    { label: 'Holdings', value: String(summary.holdings_count) },
    { label: 'Remaining cost basis', value: formatMoney(summary.remaining_cost_basis) },
  ]

  return (
    <div className={`grid gap-3 ${compact ? 'grid-cols-2 lg:grid-cols-5' : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-5'}`}>
      {cards.map((card) => (
        <article
          key={card.label}
          className={`rounded-xl border border-slate-800 bg-slate-900/40 ${compact ? 'p-3' : 'p-4'}`}
        >
          <p className="text-xs text-slate-400">{card.label}</p>
          <p className={`mt-1 font-semibold ${compact ? 'text-lg' : 'text-2xl'} ${card.className ?? 'text-slate-100'}`}>
            {card.value}
          </p>
        </article>
      ))}
    </div>
  )
}
