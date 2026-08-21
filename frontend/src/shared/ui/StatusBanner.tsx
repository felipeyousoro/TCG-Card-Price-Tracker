type StatusBannerTone = 'info' | 'success' | 'error'

const toneClass: Record<StatusBannerTone, string> = {
  info: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
  success: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
  error: 'border-red-500/40 bg-red-500/10 text-red-200',
}

export default function StatusBanner({
  tone,
  children,
}: {
  tone: StatusBannerTone
  children: string
}) {
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm ${toneClass[tone]}`}>{children}</div>
  )
}
