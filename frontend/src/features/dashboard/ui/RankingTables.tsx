import { formatMoney, formatSignedMoney } from '../../stock/model/format'
import type { DashboardByItem, DashboardItemType, RankingHoldingItem, RankingSoldItem } from '../model/types'

function pnlClass(value: number) {
  if (value > 0) return 'text-emerald-400'
  if (value < 0) return 'text-red-300'
  return 'text-slate-300'
}

function itemLabel(item: { name: string; code: string | null }) {
  return item.code ? `${item.name} (${item.code})` : item.name
}

function byType<T extends { item_type: DashboardItemType }>(rows: T[], itemType: DashboardItemType) {
  return rows.filter((row) => row.item_type === itemType)
}

function RealizedTable({ title, rows }: { title: string; rows: RankingSoldItem[] }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm font-medium text-slate-200">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-400">No sells in this range.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {rows.map((row) => (
            <li key={`${row.item_type}-${row.card_id ?? row.product_id}`} className="flex justify-between gap-3">
              <span className="truncate text-slate-200" title={itemLabel(row)}>
                {itemLabel(row)}
                <span className="ml-2 text-slate-500">×{row.quantity_sold}</span>
              </span>
              <span className={pnlClass(row.realized_gain)}>{formatSignedMoney(row.realized_gain)}</span>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}

function HoldingsTable({ title, rows }: { title: string; rows: RankingHoldingItem[] }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm font-medium text-slate-200">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-400">No current holdings.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {rows.map((row) => (
            <li key={`${row.item_type}-${row.card_id ?? row.product_id}`} className="flex justify-between gap-3">
              <span className="truncate text-slate-200" title={itemLabel(row)}>
                {itemLabel(row)}
                <span className="ml-2 text-slate-500">×{row.quantity}</span>
              </span>
              <span className="text-slate-300">{formatMoney(row.remaining_cost)}</span>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}

const GROUPS: { key: DashboardItemType; title: string }[] = [
  { key: 'card', title: 'Cards' },
  { key: 'product', title: 'Products' },
]

export default function RankingTables({ byItem }: { byItem: DashboardByItem }) {
  return (
    <div className="space-y-8">
      {GROUPS.map((group) => (
        <section key={group.key}>
          <h2 className="mb-3 text-lg font-semibold text-slate-100">{group.title}</h2>
          <div className="grid gap-4 lg:grid-cols-3">
            <RealizedTable title="Best realized gain" rows={byType(byItem.best_realized, group.key)} />
            <RealizedTable title="Worst realized gain" rows={byType(byItem.worst_realized, group.key)} />
            <HoldingsTable title="Top holdings by remaining cost" rows={byType(byItem.top_holdings, group.key)} />
          </div>
        </section>
      ))}
    </div>
  )
}
