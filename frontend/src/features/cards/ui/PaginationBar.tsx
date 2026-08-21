const buttonClass =
  'rounded-lg border border-slate-800 px-3 py-1.5 text-sm text-slate-200 transition hover:border-amber-500/40 hover:text-amber-400 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-slate-800 disabled:hover:text-slate-200'

export default function PaginationBar({
  page,
  totalCount,
  itemsPerPage,
  onPageChange,
}: {
  page: number
  totalCount: number
  itemsPerPage: number
  onPageChange: (page: number) => void
}) {
  const totalPages = Math.max(1, Math.ceil(totalCount / itemsPerPage))

  return (
    <div className="mt-8 flex items-center justify-between gap-4">
      <button type="button" className={buttonClass} disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        Previous
      </button>
      <p className="text-sm text-slate-400">
        Page {page} of {totalPages}
      </p>
      <button
        type="button"
        className={buttonClass}
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </button>
    </div>
  )
}
