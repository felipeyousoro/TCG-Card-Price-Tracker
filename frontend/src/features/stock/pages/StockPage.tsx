import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { apiErrorMessage } from '../../../shared/api/errors'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import ProductPicker from '../../products/ui/ProductPicker'
import { useDeleteTransactionMutation } from '../model/mutations'
import { useHoldings, useTransactions } from '../model/queries'
import type { HoldingItem } from '../model/types'
import BuyDialog, { type BuyTarget } from '../ui/BuyDialog'
import HoldingsTable from '../ui/HoldingsTable'
import ImportBuyHistoryForm from '../ui/ImportBuyHistoryForm'
import SellDialog, { type SellTarget } from '../ui/SellDialog'
import TransactionHistory from '../ui/TransactionHistory'

type StockTab = 'holdings' | 'history' | 'import'

const tabClass = (active: boolean) =>
  active
    ? 'border-amber-500/40 bg-amber-500/10 text-amber-200'
    : 'border-slate-800 text-slate-400 hover:text-slate-200'

export default function StockPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = parseTab(searchParams.get('tab'))
  const page = Math.max(1, Number(searchParams.get('page')) || 1)
  const holdingsQuery = useHoldings(tab === 'holdings' ? page : 1)
  const historyQuery = useTransactions(tab === 'history' ? page : 1)
  const deleteMutation = useDeleteTransactionMutation()
  const [buyTarget, setBuyTarget] = useState<BuyTarget | null>(null)
  const [sellTarget, setSellTarget] = useState<SellTarget | null>(null)
  const [showProductPicker, setShowProductPicker] = useState(false)

  const holdings = holdingsQuery.data?.data ?? []
  const transactions = historyQuery.data?.data ?? []

  function setTab(next: StockTab) {
    const params = new URLSearchParams()
    if (next !== 'holdings') params.set('tab', next)
    setSearchParams(params)
  }

  function setPage(nextPage: number) {
    const params = new URLSearchParams(searchParams)
    if (nextPage > 1) params.set('page', String(nextPage))
    else params.delete('page')
    setSearchParams(params)
  }

  const header = useMemo(() => {
    if (tab === 'history') return { title: 'Buy history', description: 'Orders grouped by store visit or online purchase.' }
    if (tab === 'import') return { title: 'Import buys', description: 'Paste one card order, review printings, then save.' }
    return { title: 'Holdings', description: 'What you own and the average you paid.' }
  }, [tab])

  function holdingToBuyTarget(item: HoldingItem): BuyTarget | null {
    if (item.item_type === 'card' && item.card_id != null) {
      return { kind: 'card', id: item.card_id, name: item.name }
    }
    if (item.item_type === 'product' && item.product_id != null) {
      return { kind: 'product', id: item.product_id, name: item.name }
    }
    return null
  }

  function holdingToSellTarget(item: HoldingItem): SellTarget | null {
    if (item.item_type === 'card' && item.card_id != null) {
      return { kind: 'card', id: item.card_id, name: item.name, maxQuantity: item.quantity }
    }
    if (item.item_type === 'product' && item.product_id != null) {
      return { kind: 'product', id: item.product_id, name: item.name, maxQuantity: item.quantity }
    }
    return null
  }

  return (
    <>
      <PageHeader title={header.title} description={header.description} />
      <div className="mb-6 flex flex-wrap gap-2">
        {(['holdings', 'history', 'import'] as const).map((value) => (
          <button
            key={value}
            type="button"
            onClick={() => setTab(value)}
            className={`rounded-lg border px-3 py-1.5 text-sm capitalize ${tabClass(tab === value)}`}
          >
            {value}
          </button>
        ))}
      </div>

      {tab === 'holdings' ? (
        <div className="space-y-4">
          <button
            type="button"
            onClick={() => setShowProductPicker((open) => !open)}
            className="text-sm text-amber-400 hover:text-amber-300"
          >
            {showProductPicker ? 'Hide product search' : 'Add product buy'}
          </button>
          {showProductPicker ? (
            <ProductPicker
              onSelect={(product) => {
                setShowProductPicker(false)
                setBuyTarget({ kind: 'product', id: product.id, name: product.name })
              }}
            />
          ) : null}
          {holdingsQuery.isLoading ? <p className="text-slate-400">Loading holdings…</p> : null}
          {holdingsQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(holdingsQuery.error)}</StatusBanner> : null}
          {holdingsQuery.data && holdings.length === 0 ? <p className="text-slate-400">No holdings yet.</p> : null}
          {holdings.length > 0 ? (
            <HoldingsTable
              items={holdings}
              page={page}
              totalCount={holdingsQuery.data?.total_count ?? 0}
              onPageChange={setPage}
              onBuy={(item) => {
                const target = holdingToBuyTarget(item)
                if (target) setBuyTarget(target)
              }}
              onSell={(item) => {
                const target = holdingToSellTarget(item)
                if (target) setSellTarget(target)
              }}
            />
          ) : null}
        </div>
      ) : null}

      {tab === 'history' ? (
        <div className="space-y-4">
          {historyQuery.isLoading ? <p className="text-slate-400">Loading history…</p> : null}
          {historyQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(historyQuery.error)}</StatusBanner> : null}
          {historyQuery.data && transactions.length === 0 ? <p className="text-slate-400">No transactions yet.</p> : null}
          {transactions.length > 0 ? (
            <TransactionHistory
              items={transactions}
              page={page}
              totalCount={historyQuery.data?.total_count ?? 0}
              onPageChange={setPage}
              isDeleting={deleteMutation.isPending}
              onDelete={(id) => deleteMutation.mutate(id)}
            />
          ) : null}
          {deleteMutation.isError ? <StatusBanner tone="error">{apiErrorMessage(deleteMutation.error)}</StatusBanner> : null}
        </div>
      ) : null}

      {tab === 'import' ? <ImportBuyHistoryForm /> : null}

      {buyTarget ? <BuyDialog target={buyTarget} onClose={() => setBuyTarget(null)} /> : null}
      {sellTarget ? <SellDialog target={sellTarget} onClose={() => setSellTarget(null)} /> : null}
    </>
  )
}

function parseTab(value: string | null): StockTab {
  if (value === 'history' || value === 'import') return value
  return 'holdings'
}
