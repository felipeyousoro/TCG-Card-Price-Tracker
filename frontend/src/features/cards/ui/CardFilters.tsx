import { useState } from 'react'

export type CardFilterValues = {
  colors: string[]
  rarities: string[]
  set_names: string[]
}

function toggleValue(selected: string[], value: string) {
  return selected.includes(value) ? selected.filter((item) => item !== value) : [...selected, value]
}

function FilterSection({
  title,
  options,
  selected,
  onChange,
}: {
  title: string
  options: string[]
  selected: string[]
  onChange: (next: string[]) => void
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border-b border-slate-800 last:border-b-0">
      <button
        type="button"
        className="flex w-full items-center justify-between gap-2 py-2 text-left text-sm text-slate-200 transition hover:text-amber-400"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>
          {title}
          {selected.length > 0 ? (
            <span className="ml-1 text-slate-500">({selected.length})</span>
          ) : null}
        </span>
        <span className="text-slate-500">{open ? '−' : '+'}</span>
      </button>
      {open ? (
        <ul className="max-h-56 space-y-1 overflow-y-auto pb-3">
          {options.map((option) => (
            <li key={option}>
              <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  className="mt-0.5 rounded border-slate-600 bg-slate-900 text-amber-500"
                  checked={selected.includes(option)}
                  onChange={() => onChange(toggleValue(selected, option))}
                />
                <span>{option}</span>
              </label>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
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
    <aside className="mb-6 shrink-0 rounded-lg border border-slate-800 bg-slate-900/40 px-3 py-1 lg:mb-0 lg:w-64">
      <FilterSection
        title="Color"
        options={colors}
        selected={values.colors}
        onChange={(next) => onChange({ ...values, colors: next })}
      />
      <FilterSection
        title="Rarity"
        options={rarities}
        selected={values.rarities}
        onChange={(next) => onChange({ ...values, rarities: next })}
      />
      <FilterSection
        title="Set"
        options={setNames}
        selected={values.set_names}
        onChange={(next) => onChange({ ...values, set_names: next })}
      />
    </aside>
  )
}
