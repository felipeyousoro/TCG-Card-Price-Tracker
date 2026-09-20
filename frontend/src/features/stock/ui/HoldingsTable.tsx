import CardTile from '../../cards/ui/CardTile'
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
  onSell,
}: {
  items: HoldingItem[]
  page: number
  totalCount: number
  onPageChange: (page: number) => void
  onBuy: (item: HoldingItem) => void
  onSell: (item: HoldingItem) => void
}) {
  return (
    <>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {items.map((item) => (
          <CardTile
            key={`${item.item_type}-${item.card_id ?? item.product_id}`}
            image_url={item.image_url}
            name={item.name}
            code={item.code ?? item.item_type}
            ownedQuantity={item.quantity}
            avgCost={formatMoney(item.avg_unit_cost)}
            buyLabel="Buy more"
            onBuy={() => onBuy(item)}
            onSell={() => onSell(item)}
          />
        ))}
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
