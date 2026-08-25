import PaginationBar from '../../cards/ui/PaginationBar'
import { formatMoney } from '../model/format'
import type { StockTransaction } from '../model/types'
import { HISTORY_PAGE_SIZE } from '../model/types'

export default function TransactionHistory({
  items,
  page,
  totalCount,
  onPageChange,
  onDelete,
  isDeleting,
}: {
  items: StockTransaction[]
  page: number
  totalCount: number
  onPageChange: (page: number) => void
  onDelete: (id: string) => void
  isDeleting: boolean
}) {
  return (
    <div className="space-y-4">
      {items.map((transaction) => (
        <article key={transaction.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <div className="mb-3 flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-100">
                {transaction.transaction_date} · {transaction.transaction_type}
              </p>
              {transaction.shipping_cost > 0 ? (
                <p className="mt-1 text-sm text-slate-400">Shipping {formatMoney(transaction.shipping_cost)}</p>
              ) : null}
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-200">{formatMoney(transaction.total)}</p>
              {transaction.transaction_type === 'buy' ? (
                <button
                  type="button"
                  disabled={isDeleting}
                  onClick={() => onDelete(transaction.id)}
                  className="mt-1 text-xs text-red-300 hover:text-red-200 disabled:opacity-60"
                >
                  Delete
                </button>
              ) : null}
            </div>
          </div>
          <ul className="space-y-1 text-sm text-slate-300">
            {transaction.lines.map((line) => (
              <li key={line.id} className="flex justify-between gap-3">
                <span>
                  {line.quantity}× {line.name}
                </span>
                <span className="text-slate-400">{formatMoney(line.line_total)}</span>
              </li>
            ))}
          </ul>
        </article>
      ))}
      {totalCount > 0 ? (
        <PaginationBar
          page={page}
          totalCount={totalCount}
          itemsPerPage={HISTORY_PAGE_SIZE}
          onPageChange={onPageChange}
        />
      ) : null}
    </div>
  )
}
