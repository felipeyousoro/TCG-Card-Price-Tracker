export default function CardTile({
  image_url,
  name,
  code,
  rarity,
  ownedQuantity = 0,
  isFavorite = false,
  onBuy,
  onToggleFavorite,
}: {
  image_url: string | null
  name: string
  code: string
  rarity?: string
  ownedQuantity?: number
  isFavorite?: boolean
  onBuy?: () => void
  onToggleFavorite?: () => void
}) {
  return (
    <article className="relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
      {ownedQuantity > 0 ? (
        <span className="absolute left-2 top-2 rounded-full bg-slate-950/80 px-2 py-0.5 text-xs font-medium text-amber-300">
          ×{ownedQuantity}
        </span>
      ) : null}
      {onToggleFavorite ? (
        <button
          type="button"
          onClick={onToggleFavorite}
          aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          className={`absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-0.5 text-sm ${
            isFavorite ? 'text-rose-400' : 'text-slate-400 hover:text-rose-300'
          }`}
        >
          {isFavorite ? '♥' : '♡'}
        </button>
      ) : null}
      {image_url ? (
        <img src={image_url} alt={name} className="aspect-[63/88] w-full object-cover bg-slate-800" />
      ) : (
        <div className="flex aspect-[63/88] w-full items-center justify-center bg-slate-800 text-xs text-slate-500">
          No image
        </div>
      )}
      <div className="space-y-2 px-3 py-2">
        <p className="truncate text-sm font-medium text-slate-100" title={name}>
          {name}
        </p>
        <p className="truncate text-xs text-slate-400" title={rarity ? `${code} · ${rarity}` : code}>
          {rarity ? `${code} · ${rarity}` : code}
        </p>
        {onBuy ? (
          <button
            type="button"
            onClick={onBuy}
            className="w-full rounded-md border border-slate-700 py-1 text-xs text-amber-400 transition hover:border-amber-500/40"
          >
            Buy
          </button>
        ) : null}
      </div>
    </article>
  )
}
