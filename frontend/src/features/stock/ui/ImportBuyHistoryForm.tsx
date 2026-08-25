import { type FormEvent, useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useImportBuysMutation } from '../model/mutations'
import { todayISODate } from '../model/format'
import type { BuyImportResult } from '../model/types'

const fieldClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'

export default function ImportBuyHistoryForm() {
  const importMutation = useImportBuysMutation()
  const [result, setResult] = useState<BuyImportResult | null>(null)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    importMutation.mutate(
      {
        transaction_date: String(form.get('transaction_date')),
        shipping_cost: Number(form.get('shipping_cost') || 0),
        text: String(form.get('text') ?? ''),
      },
      { onSuccess: setResult },
    )
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-3 text-sm text-slate-400">
        <p>One paste is one order of catalog cards. Split fields with semicolons:</p>
        <pre className="mt-3 overflow-x-auto text-xs text-slate-300">{`card_set_id;variant;quantity;unit_price
OP01-001;;3;4.50
OP16-003;SEC;1;12.00`}</pre>
        <p className="mt-3">
          card_set_id is required. Leave variant empty unless several printings share that number, then use name or
          rarity (for example SEC). Products are not imported here.
        </p>
      </div>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <label className="block text-sm">
          <span className="mb-1.5 block text-slate-400">Order date</span>
          <input name="transaction_date" type="date" required defaultValue={todayISODate()} className={fieldClass} />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block text-slate-400">Total shipping</span>
          <input name="shipping_cost" type="number" min={0} step="0.01" defaultValue="0.00" className={fieldClass} />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block text-slate-400">Line items</span>
          <textarea name="text" required rows={8} className={fieldClass} />
        </label>
        {importMutation.isError ? <StatusBanner tone="error">{apiErrorMessage(importMutation.error)}</StatusBanner> : null}
        <button
          type="submit"
          disabled={importMutation.isPending}
          className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20 disabled:opacity-60"
        >
          {importMutation.isPending ? 'Importing…' : 'Import order'}
        </button>
      </form>
      {result ? (
        <div className="space-y-3">
          <dl className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <dt className="text-slate-400">Fetched</dt>
              <dd className="text-lg font-semibold text-slate-100">{result.fetched}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Inserted</dt>
              <dd className="text-lg font-semibold text-slate-100">{result.inserted}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Skipped</dt>
              <dd className="text-lg font-semibold text-slate-100">{result.skipped}</dd>
            </div>
          </dl>
          {result.errors.length > 0 ? (
            <ul className="space-y-1 text-sm text-red-300">
              {result.errors.map((item) => (
                <li key={`${item.line}-${item.message}`}>
                  Line {item.line}: {item.message}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
