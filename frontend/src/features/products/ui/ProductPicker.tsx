import { useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import { useCreateProductMutation } from '../model/mutations'
import { useProductSearch } from '../model/queries'
import type { ProductListItem } from '../model/types'
import ProductForm from './ProductForm'

export default function ProductPicker({
  onSelect,
}: {
  onSelect: (product: ProductListItem) => void
}) {
  const [query, setQuery] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const search = useProductSearch(query.trim())
  const createMutation = useCreateProductMutation()
  const matches = search.data?.data ?? []

  return (
    <div className="space-y-4">
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Search products</span>
        <input
          value={query}
          onChange={(event) => {
            setQuery(event.target.value)
            setShowCreate(false)
          }}
          placeholder="OP-10 Booster Box"
          className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60"
        />
      </label>
      {search.isFetching ? <p className="text-sm text-slate-400">Searching…</p> : null}
      {matches.length > 0 ? (
        <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800">
          {matches.map((product) => (
            <li key={product.id}>
              <button
                type="button"
                onClick={() => onSelect(product)}
                className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-slate-800/80"
              >
                <span>{product.name}</span>
                <span className="text-slate-500">{product.category}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {query.trim() && !search.isFetching && matches.length === 0 ? (
        <p className="text-sm text-slate-400">No matches. Create a new catalog product below.</p>
      ) : null}
      {query.trim() && matches.length === 0 ? (
        showCreate ? (
          <ProductForm
            isPending={createMutation.isPending}
            error={createMutation.isError ? apiErrorMessage(createMutation.error) : undefined}
            onSubmit={(payload) => {
              createMutation.mutate(payload, {
                onSuccess: (created) => onSelect(created),
              })
            }}
          />
        ) : (
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="text-sm text-amber-400 hover:text-amber-300"
          >
            Create new product
          </button>
        )
      ) : null}
    </div>
  )
}
