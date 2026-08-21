export default function CardTile({
  image_url,
  name,
  code,
}: {
  image_url: string | null
  name: string
  code: string
}) {
  return (
    <article className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
      {image_url ? (
        <img src={image_url} alt={name} className="aspect-[63/88] w-full object-cover bg-slate-800" />
      ) : (
        <div className="flex aspect-[63/88] w-full items-center justify-center bg-slate-800 text-xs text-slate-500">
          No image
        </div>
      )}
      <div className="space-y-1 px-3 py-2">
        <p className="truncate text-sm font-medium text-slate-100" title={name}>
          {name}
        </p>
        <p className="truncate text-xs text-slate-400" title={code}>
          {code}
        </p>
      </div>
    </article>
  )
}
