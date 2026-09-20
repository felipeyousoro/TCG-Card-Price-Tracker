import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { apiErrorMessage } from '../../../shared/api/errors'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import PaginationBar from '../../cards/ui/PaginationBar'
import CardTile from '../../cards/ui/CardTile'
import BuyDialog, { type BuyTarget } from '../../stock/ui/BuyDialog'
import SellDialog, { type SellTarget } from '../../stock/ui/SellDialog'
import { useStockQuantities } from '../../stock/model/queries'
import { useToggleCardFavorite, useToggleProductFavorite } from '../model/mutations'
import { useFavoritesList } from '../model/queries'
import { FAVORITES_PAGE_SIZE } from '../model/types'

export default function FavoritesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const pageRaw = Number(searchParams.get('page'))
  const page = Number.isInteger(pageRaw) && pageRaw > 0 ? pageRaw : 1
  const listQuery = useFavoritesList(page)
  const quantitiesQuery = useStockQuantities()
  const toggleCard = useToggleCardFavorite()
  const toggleProduct = useToggleProductFavorite()
  const [buyTarget, setBuyTarget] = useState<BuyTarget | null>(null)
  const [sellTarget, setSellTarget] = useState<SellTarget | null>(null)

  const items = listQuery.data?.data ?? []
  const totalCount = listQuery.data?.total_count ?? 0

  return (
    <>
      <PageHeader title="Favorites" description="Cards and products you have starred." />
      {listQuery.isLoading ? <p className="text-slate-400">Loading favorites…</p> : null}
      {listQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(listQuery.error)}</StatusBanner> : null}
      {listQuery.data && items.length === 0 ? <p className="text-slate-400">No favorites yet.</p> : null}
      {items.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {items.map((item) => {
            const isCard = item.card_id != null
            const owned = isCard
              ? (quantitiesQuery.data?.cards[String(item.card_id)] ?? 0)
              : (quantitiesQuery.data?.products[String(item.product_id)] ?? 0)
            return (
              <CardTile
                key={item.id}
                image_url={item.image_url}
                name={item.name}
                code={item.code ?? ''}
                ownedQuantity={owned}
                isFavorite
                onBuy={
                  item.card_id != null
                    ? () => setBuyTarget({ kind: 'card', id: item.card_id as number, name: item.name })
                    : item.product_id != null
                      ? () => setBuyTarget({ kind: 'product', id: item.product_id as number, name: item.name })
                      : undefined
                }
                onSell={
                  owned > 0
                    ? item.card_id != null
                      ? () =>
                          setSellTarget({
                            kind: 'card',
                            id: item.card_id as number,
                            name: item.name,
                            maxQuantity: owned,
                          })
                      : item.product_id != null
                        ? () =>
                            setSellTarget({
                              kind: 'product',
                              id: item.product_id as number,
                              name: item.name,
                              maxQuantity: owned,
                            })
                        : undefined
                    : undefined
                }
                onToggleFavorite={() => {
                  if (item.card_id != null) {
                    toggleCard.mutate({ cardId: item.card_id, isFavorite: true })
                  } else if (item.product_id != null) {
                    toggleProduct.mutate({ productId: item.product_id, isFavorite: true })
                  }
                }}
              />
            )
          })}
        </div>
      ) : null}
      {listQuery.data && totalCount > 0 ? (
        <PaginationBar
          page={page}
          totalCount={totalCount}
          itemsPerPage={FAVORITES_PAGE_SIZE}
          onPageChange={(next) => {
            const params = new URLSearchParams()
            if (next > 1) params.set('page', String(next))
            setSearchParams(params)
          }}
        />
      ) : null}
      {buyTarget ? <BuyDialog target={buyTarget} onClose={() => setBuyTarget(null)} /> : null}
      {sellTarget ? <SellDialog target={sellTarget} onClose={() => setSellTarget(null)} /> : null}
    </>
  )
}
