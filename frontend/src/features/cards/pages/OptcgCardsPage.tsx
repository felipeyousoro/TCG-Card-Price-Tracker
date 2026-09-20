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
import type { OptcgCardListParams, OptcgCardSort } from '../model/types'
import { nextOptcgSort, OPTCG_PAGE_SIZE, OPTCG_SORT_LABEL } from '../model/types'
import CardFilters, { type CardFilterValues } from '../ui/CardFilters'
import CardTile from '../ui/CardTile'
import PaginationBar from '../ui/PaginationBar'

const inputClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'
const toolbarButtonClass =
  'rounded-lg border border-slate-800 px-3 py-2 text-sm text-slate-200 transition hover:border-amber-500/40 hover:text-amber-400'
const toolbarButtonActiveClass =
  'rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20'

function uniqueSorted(values: string[]) {
  return [...new Set(values.filter(Boolean))].sort()
}

function readSort(value: string | null): OptcgCardSort {
  if (value === 'number' || value === 'number_desc') return value
  return 'set'
}

function readListParams(searchParams: URLSearchParams): OptcgCardListParams {
  const pageRaw = Number(searchParams.get('page'))
  return {
    page: Number.isInteger(pageRaw) && pageRaw > 0 ? pageRaw : 1,
    name: searchParams.get('name') ?? '',
    colors: uniqueSorted(searchParams.getAll('color')),
    rarities: uniqueSorted(searchParams.getAll('rarity')),
    set_names: uniqueSorted(searchParams.getAll('set_name')),
    base_only: searchParams.get('base_only') === '1',
    sort: readSort(searchParams.get('sort')),
  }
}

function toSearchParams(params: OptcgCardListParams) {
  const next = new URLSearchParams()
  if (params.page > 1) next.set('page', String(params.page))
  if (params.name) next.set('name', params.name)
  for (const color of uniqueSorted(params.colors)) next.append('color', color)
  for (const rarity of uniqueSorted(params.rarities)) next.append('rarity', rarity)
  for (const setName of uniqueSorted(params.set_names)) next.append('set_name', setName)
  if (params.base_only) next.set('base_only', '1')
  if (params.sort !== 'set') next.set('sort', params.sort)
  return next
}

function sameStringList(left: string[], right: string[]) {
  if (left.length !== right.length) return false
  return left.every((value, index) => value === right[index])
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
  const paramsRef = useRef(params)
  paramsRef.current = params

  useEffect(() => {
    if (params.name === debouncedNameRef.current) return
    setNameInput(params.name)
  }, [params.name])

  function updateParams(next: OptcgCardListParams) {
    setSearchParams(toSearchParams(next))
  }

  useEffect(() => {
    const current = paramsRef.current
    if (debouncedName === current.name) return
    setSearchParams(
      toSearchParams({
        ...current,
        page: 1,
        name: debouncedName,
      }),
    )
  }, [debouncedName, setSearchParams])

  function handleFilterChange(values: CardFilterValues) {
    const filtersChanged =
      !sameStringList(uniqueSorted(values.colors), params.colors) ||
      !sameStringList(uniqueSorted(values.rarities), params.rarities) ||
      !sameStringList(uniqueSorted(values.set_names), params.set_names)
    if (filtersChanged) {
      updateParams({
        ...params,
        name: nameInput,
        colors: uniqueSorted(values.colors),
        rarities: uniqueSorted(values.rarities),
        set_names: uniqueSorted(values.set_names),
        page: 1,
      })
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
      <div className="lg:flex lg:items-start lg:gap-6">
        <CardFilters
          colors={filtersQuery.data?.colors ?? []}
          rarities={filtersQuery.data?.rarities ?? []}
          setNames={filtersQuery.data?.set_names ?? []}
          values={{ colors: params.colors, rarities: params.rarities, set_names: params.set_names }}
          onChange={handleFilterChange}
        />
        <div className="min-w-0 flex-1">
          <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="block min-w-0 flex-1 text-sm">
              <span className="mb-1.5 block text-slate-400">Search by name</span>
              <input
                className={inputClass}
                value={nameInput}
                onChange={(event) => setNameInput(event.target.value)}
                placeholder="Luffy"
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className={params.base_only ? toolbarButtonActiveClass : toolbarButtonClass}
                onClick={() =>
                  updateParams({ ...params, name: nameInput, page: 1, base_only: !params.base_only })
                }
              >
                Base cards
              </button>
              <button
                type="button"
                className={toolbarButtonClass}
                onClick={() =>
                  updateParams({ ...params, name: nameInput, page: 1, sort: nextOptcgSort(params.sort) })
                }
              >
                {OPTCG_SORT_LABEL[params.sort]}
              </button>
            </div>
          </div>
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
        </div>
      </div>
      {buyTarget ? <BuyDialog target={buyTarget} onClose={() => setBuyTarget(null)} /> : null}
    </>
  )
}
