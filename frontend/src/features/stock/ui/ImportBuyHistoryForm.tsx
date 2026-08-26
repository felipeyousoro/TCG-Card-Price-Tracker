import { useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useCreateTransactionMutation, usePreviewImportMutation } from '../model/mutations'
import { formatMoney, todayISODate } from '../model/format'
import type { ImportPreviewLine, ImportPreviewMatch } from '../model/types'

const fieldClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'

type PreviewRow = ImportPreviewLine & { rowId: string }

function versionLabel(match: ImportPreviewMatch, matches: ImportPreviewMatch[]) {
  const rarityClash = matches.filter((item) => item.rarity === match.rarity).length > 1
  const base = `${match.card_number} · ${match.rarity}`
  return rarityClash ? `${base} · ${match.name}` : base
}

function selectedMatch(row: PreviewRow) {
  return row.matches.find((item) => item.card_id === row.selected_card_id) ?? row.matches[0]
}

export default function ImportBuyHistoryForm() {
  const previewMutation = usePreviewImportMutation()
  const saveMutation = useCreateTransactionMutation()
  const [transactionDate, setTransactionDate] = useState(todayISODate)
  const [shippingCost, setShippingCost] = useState('0.00')
  const [text, setText] = useState('')
  const [rows, setRows] = useState<PreviewRow[]>([])
  const [saved, setSaved] = useState(false)

  function handleImport() {
    setSaved(false)
    previewMutation.mutate(
      { text },
      {
        onSuccess: (result) => {
          setText(result.unmatched_text)
          setRows((current) => [
            ...current,
            ...result.lines.map((line) => ({ ...line, rowId: crypto.randomUUID() })),
          ])
        },
      },
    )
  }

  function handleVersionChange(rowId: string, cardId: number) {
    setRows((current) =>
      current.map((row) =>
        row.rowId === rowId ? { ...row, selected_card_id: cardId, auto_chosen: false } : row,
      ),
    )
  }

  function handleSave() {
    if (rows.length === 0) return
    setSaved(false)
    saveMutation.mutate(
      {
        transaction_date: transactionDate,
        shipping_cost: Number(shippingCost || 0),
        lines: rows.map((row) => ({
          card_id: row.selected_card_id,
          quantity: row.quantity,
          unit_price: row.unit_price,
        })),
      },
      {
        onSuccess: () => {
          setRows([])
          setSaved(true)
        },
      },
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
          card_set_id is required. Leave variant empty unless several printings share that number, then
          use name or rarity (for example SEC). Products are not imported here.
        </p>
        <p className="mt-3">
          Import resolves catalog cards into the table. Parallel printings are auto-picked; you can
          change the version before Save. Lines that cannot be matched stay in the paste box.
        </p>
      </div>
      <div className="space-y-3">
        <label className="block text-sm">
          <span className="mb-1.5 block text-slate-400">Order date</span>
          <input
            name="transaction_date"
            type="date"
            required
            value={transactionDate}
            onChange={(event) => setTransactionDate(event.target.value)}
            className={fieldClass}
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block text-slate-400">Total shipping</span>
          <input
            name="shipping_cost"
            type="number"
            min={0}
            step="0.01"
            value={shippingCost}
            onChange={(event) => setShippingCost(event.target.value)}
            className={fieldClass}
          />
        </label>
        <div className="text-sm">
          <span className="mb-1.5 block text-slate-400">Line items</span>
          <div className="flex items-start gap-2">
            <textarea
              name="text"
              rows={8}
              value={text}
              onChange={(event) => setText(event.target.value)}
              className={fieldClass}
            />
            <button
              type="button"
              disabled={previewMutation.isPending || !text.trim()}
              onClick={handleImport}
              className="shrink-0 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20 disabled:opacity-60"
            >
              {previewMutation.isPending ? 'Importing…' : 'Import'}
            </button>
          </div>
        </div>
        {previewMutation.isError ? (
          <StatusBanner tone="error">{apiErrorMessage(previewMutation.error)}</StatusBanner>
        ) : null}
      </div>
      {rows.length > 0 ? (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-800 bg-slate-900/80 text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Card</th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Version</th>
                <th className="px-4 py-3 font-medium">Price</th>
                <th className="px-4 py-3 font-medium">Qty</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const match = selectedMatch(row)
                return (
                  <tr key={row.rowId} className="border-b border-slate-800 last:border-0">
                    <td className="px-4 py-3">
                      {match.image_url ? (
                        <img
                          src={match.image_url}
                          alt={match.name}
                          className="h-16 w-11 rounded object-cover bg-slate-800"
                        />
                      ) : (
                        <div className="h-16 w-11 rounded bg-slate-800" />
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-100">{match.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <select
                          value={row.selected_card_id}
                          onChange={(event) => handleVersionChange(row.rowId, Number(event.target.value))}
                          className={fieldClass}
                        >
                          {row.matches.map((item) => (
                            <option key={item.card_id} value={item.card_id}>
                              {versionLabel(item, row.matches)}
                            </option>
                          ))}
                        </select>
                        {row.auto_chosen ? (
                          <span
                            title="Auto-chosen"
                            className="inline-flex h-5 w-5 shrink-0 cursor-default items-center justify-center rounded-full border border-amber-500/40 text-[10px] font-medium text-amber-200"
                          >
                            i
                          </span>
                        ) : null}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-200">{formatMoney(row.unit_price)}</td>
                    <td className="px-4 py-3 text-slate-200">{row.quantity}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : null}
      {saveMutation.isError ? (
        <StatusBanner tone="error">{apiErrorMessage(saveMutation.error)}</StatusBanner>
      ) : null}
      {saved ? <StatusBanner tone="success">Order saved.</StatusBanner> : null}
      <button
        type="button"
        disabled={saveMutation.isPending || rows.length === 0}
        onClick={handleSave}
        className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20 disabled:opacity-60"
      >
        {saveMutation.isPending ? 'Saving…' : 'Save'}
      </button>
    </div>
  )
}
