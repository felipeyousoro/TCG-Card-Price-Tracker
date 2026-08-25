import PaginationBar from '../../cards/ui/PaginationBar'
import { formatMoney } from '../model/format'
import type { HoldingItem } from '../model/types'
import { STOCK_PAGE_SIZE } from '../model/types'

export default function HoldingsTable({
  items,
  page,
  totalCount,
  onPageChange,
  onBuy,
}: {
  items: HoldingItem[]
  page: number
  totalCount: number
  onPageChange: (page: number) => void
  onBuy: (item: HoldingItem) => void
}) {
  return (
    <>
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-800 bg-slate-900/80 text-slate-400">
            <tr>
              <th className="px-4 py-3 font-medium">Item</th>
              <th className="px-4 py-3 font-medium">Qty</th>
              <th className="px-4 py-3 font-medium">Avg cost</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={`${item.item_type}-${item.card_id ?? item.product_id}`} className="border-b border-slate-800 last:border-0">
                <td className="px-4 py-3">
                  <p className="text-slate-100">{item.name}</p>
                  <p className="text-xs text-slate-500">{item.code ?? item.item_type}</p>
                </td>
                <td className="px-4 py-3 text-slate-200">{item.quantity}</td>
                <td className="px-4 py-3 text-slate-200">{formatMoney(item.avg_unit_cost)}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={() => onBuy(item)}
                    className="text-amber-400 hover:text-amber-300"
                  >
                    Buy more
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalCount > 0 ? (
        <PaginationBar
          page={page}
          totalCount={totalCount}
          itemsPerPage={STOCK_PAGE_SIZE}
          onPageChange={onPageChange}
        />
      ) : null}
    </>
  )
}
