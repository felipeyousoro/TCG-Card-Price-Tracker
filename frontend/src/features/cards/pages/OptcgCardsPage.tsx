import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { apiErrorMessage } from '../../../shared/api/errors'
import { useDebouncedValue } from '../../../shared/lib/useDebouncedValue'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useToggleCardFavorite } from '../../favorites/model/mutations'
import { useFavoriteIds } from '../../favorites/model/queries'
import BuyDialog, { type BuyTarget } from '../../stock/ui/BuyDialog'
import { useStockQuantities } from '../../stock/model/queries'
import { useOptcgCardFilters, useOptcgCardList } from '../model/queries'
import type { OptcgCardListParams } from '../model/types'
import { OPTCG_PAGE_SIZE } from '../model/types'
import CardFilters, { type CardFilterValues } from '../ui/CardFilters'
import CardTile from '../ui/CardTile'
import PaginationBar from '../ui/PaginationBar'

function readListParams(searchParams: URLSearchParams): OptcgCardListParams {
  const pageRaw = Number(searchParams.get('page'))
  return {
    page: Number.isInteger(pageRaw) && pageRaw > 0 ? pageRaw : 1,
    name: searchParams.get('name') ?? '',
    color: searchParams.get('color') ?? '',
    rarity: searchParams.get('rarity') ?? '',
    set_name: searchParams.get('set_name') ?? '',
  }
}

function toSearchParams(params: OptcgCardListParams) {
  const next = new URLSearchParams()
  if (params.page > 1) next.set('page', String(params.page))
  if (params.name) next.set('name', params.name)
  if (params.color) next.set('color', params.color)
  if (params.rarity) next.set('rarity', params.rarity)
  if (params.set_name) next.set('set_name', params.set_name)
  return next
}

export default function OptcgCardsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const params = readListParams(searchParams)
  const [nameInput, setNameInput] = useState(params.name)
  const debouncedName = useDebouncedValue(nameInput, 300)
  const debouncedNameRef = useRef(debouncedName)
  debouncedNameRef.current = debouncedName
  const listParams = { ...params, name: debouncedName }
  const filtersQuery = useOptcgCardFilters()
  const listQuery = useOptcgCardList(listParams)
  const quantitiesQuery = useStockQuantities()
  const favoriteIdsQuery = useFavoriteIds()
  const toggleFavorite = useToggleCardFavorite()
  const [buyTarget, setBuyTarget] = useState<BuyTarget | null>(null)

  useEffect(() => {
    if (params.name === debouncedNameRef.current) return
    setNameInput(params.name)
  }, [params.name])

  function updateParams(next: OptcgCardListParams) {
    setSearchParams(toSearchParams(next))
  }

  useEffect(() => {
    if (debouncedName === params.name) return
    setSearchParams(
      toSearchParams({
        page: 1,
        name: debouncedName,
        color: params.color,
        rarity: params.rarity,
        set_name: params.set_name,
      }),
    )
  }, [debouncedName, params.color, params.name, params.rarity, params.set_name, setSearchParams])

  function handleFilterChange(values: CardFilterValues) {
    const filtersChanged =
      values.color !== params.color || values.rarity !== params.rarity || values.set_name !== params.set_name
    setNameInput(values.name)
    if (filtersChanged) {
      updateParams({ ...values, page: 1 })
    }
  }

  const cards = listQuery.data?.data ?? []
  const totalCount = listQuery.data?.total_count ?? 0
  const favoriteCardIds = new Set(favoriteIdsQuery.data?.card_ids ?? [])

  return (
    <>
      <PageHeader title="One Piece TCG" description="Browse catalog cards, 50 per page." />
      {filtersQuery.isError ? (
        <div className="mb-6">
          <StatusBanner tone="error">{apiErrorMessage(filtersQuery.error)}</StatusBanner>
        </div>
      ) : null}
      <CardFilters
        colors={filtersQuery.data?.colors ?? []}
        rarities={filtersQuery.data?.rarities ?? []}
        setNames={filtersQuery.data?.set_names ?? []}
        values={{ name: nameInput, color: params.color, rarity: params.rarity, set_name: params.set_name }}
        onChange={handleFilterChange}
      />
      {listQuery.isLoading ? <p className="text-slate-400">Loading cards…</p> : null}
      {listQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(listQuery.error)}</StatusBanner> : null}
      {listQuery.data && cards.length === 0 ? (
        <p className="text-slate-400">No cards match the current filters.</p>
      ) : null}
      {cards.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {cards.map((card) => (
            <CardTile
              key={card.id}
              image_url={card.card_image}
              name={card.card_name}
              code={card.card_set_id}
              rarity={card.rarity}
              ownedQuantity={quantitiesQuery.data?.cards[String(card.id)] ?? 0}
              isFavorite={favoriteCardIds.has(card.id)}
              onBuy={() => setBuyTarget({ kind: 'card', id: card.id, name: card.card_name })}
              onToggleFavorite={() =>
                toggleFavorite.mutate({ cardId: card.id, isFavorite: favoriteCardIds.has(card.id) })
              }
            />
          ))}
        </div>
      ) : null}
      {listQuery.data && totalCount > 0 ? (
        <PaginationBar
          page={params.page}
          totalCount={totalCount}
          itemsPerPage={OPTCG_PAGE_SIZE}
          onPageChange={(page) => updateParams({ ...params, name: debouncedName, page })}
        />
      ) : null}
      {buyTarget ? <BuyDialog target={buyTarget} onClose={() => setBuyTarget(null)} /> : null}
    </>
  )
}
