import { type FormEvent, useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import { todayISODate } from '../model/format'
import { useSellCardMutation, useSellProductMutation } from '../model/mutations'

const fieldClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'

export type SellTarget =
  | { kind: 'card'; id: number; name: string; maxQuantity: number }
  | { kind: 'product'; id: number; name: string; maxQuantity: number }

export default function SellDialog({
  target,
  onClose,
}: {
  target: SellTarget
  onClose: () => void
}) {
  const sellCard = useSellCardMutation()
  const sellProduct = useSellProductMutation()
  const [error, setError] = useState<string | undefined>()
  const isPending = sellCard.isPending || sellProduct.isPending

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const quantity = Number(form.get('quantity'))
    const unitPrice = Number(form.get('unit_price'))
    const transactionDate = String(form.get('transaction_date'))
    if (quantity > target.maxQuantity) {
      setError(`You only own ${target.maxQuantity}.`)
      return
    }
    const payload = {
      quantity,
      unit_price: unitPrice,
      transaction_date: transactionDate,
    }

    const onSuccess = () => onClose()
    const onError = (err: unknown) => setError(apiErrorMessage(err))

    if (target.kind === 'card') {
      sellCard.mutate({ cardId: target.id, payload }, { onSuccess, onError })
    } else {
      sellProduct.mutate({ productId: target.id, payload }, { onSuccess, onError })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">Record sell</h2>
            <p className="mt-1 text-sm text-slate-400">{target.name}</p>
            <p className="mt-1 text-xs text-slate-500">Owned: {target.maxQuantity}</p>
          </div>
          <button type="button" onClick={onClose} className="text-sm text-slate-400 hover:text-slate-200">
            Close
          </button>
        </div>
        <form className="space-y-3" onSubmit={handleSubmit}>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-400">Date</span>
            <input name="transaction_date" type="date" required defaultValue={todayISODate()} className={fieldClass} />
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-400">Quantity</span>
            <input
              name="quantity"
              type="number"
              min={1}
              max={target.maxQuantity}
              step={1}
              required
              defaultValue={1}
              className={fieldClass}
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-400">Unit price</span>
            <input name="unit_price" type="number" min={0} step="0.01" required defaultValue="0.00" className={fieldClass} />
          </label>
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
          <button
            type="submit"
            disabled={isPending}
            className="w-full rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20 disabled:opacity-60"
          >
            {isPending ? 'Saving…' : 'Save sell'}
          </button>
        </form>
      </div>
    </div>
  )
}
