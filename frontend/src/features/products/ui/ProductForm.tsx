import type { FormEvent } from 'react'

import type { ProductCategory, ProductCreate } from '../model/types'
import { PRODUCT_CATEGORIES } from '../model/types'

const fieldClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'

export default function ProductForm({
  onSubmit,
  isPending,
  error,
}: {
  onSubmit: (payload: ProductCreate) => void
  isPending: boolean
  error?: string
}) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const name = String(form.get('name') ?? '').trim()
    if (!name) return
    onSubmit({
      name,
      category: String(form.get('category') ?? 'other') as ProductCategory,
      set_name: String(form.get('set_name') ?? '').trim() || null,
      image_url: String(form.get('image_url') ?? '').trim() || null,
    })
  }

  return (
    <form className="space-y-3" onSubmit={handleSubmit}>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Name</span>
        <input name="name" required className={fieldClass} />
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Category</span>
        <select name="category" defaultValue="other" className={fieldClass}>
          {PRODUCT_CATEGORIES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Set name (optional)</span>
        <input name="set_name" className={fieldClass} />
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Image URL (optional)</span>
        <input name="image_url" className={fieldClass} />
      </label>
      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      <button
        type="submit"
        disabled={isPending}
        className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20 disabled:opacity-60"
      >
        {isPending ? 'Saving…' : 'Create product'}
      </button>
    </form>
  )
}
