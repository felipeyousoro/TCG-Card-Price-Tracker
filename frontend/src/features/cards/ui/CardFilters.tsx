const selectClass =
  'w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-amber-500/60'

export type CardFilterValues = {
  color: string
  rarity: string
  set_name: string
}

export default function CardFilters({
  colors,
  rarities,
  setNames,
  values,
  onChange,
}: {
  colors: string[]
  rarities: string[]
  setNames: string[]
  values: CardFilterValues
  onChange: (next: CardFilterValues) => void
}) {
  return (
    <div className="mb-6 grid gap-4 sm:grid-cols-3">
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Color</span>
        <select
          className={selectClass}
          value={values.color}
          onChange={(event) => onChange({ ...values, color: event.target.value })}
        >
          <option value="">All</option>
          {colors.map((color) => (
            <option key={color} value={color}>
              {color}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Rarity</span>
        <select
          className={selectClass}
          value={values.rarity}
          onChange={(event) => onChange({ ...values, rarity: event.target.value })}
        >
          <option value="">All</option>
          {rarities.map((rarity) => (
            <option key={rarity} value={rarity}>
              {rarity}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block text-slate-400">Set</span>
        <select
          className={selectClass}
          value={values.set_name}
          onChange={(event) => onChange({ ...values, set_name: event.target.value })}
        >
          <option value="">All</option>
          {setNames.map((setName) => (
            <option key={setName} value={setName}>
              {setName}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}
