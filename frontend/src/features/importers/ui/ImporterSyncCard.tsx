import StatusBanner from '../../../shared/ui/StatusBanner'
import type { ImporterRun } from '../model/types'
import ImporterJobLog from './ImporterJobLog'
import ImportResultPanel from './ImportResultPanel'

export default function ImporterSyncCard({
  label,
  description,
  run,
  isStarting,
  startError,
  onSync,
}: {
  label: string
  description: string
  run: ImporterRun
  isStarting: boolean
  startError?: string
  onSync: () => void
}) {
  const busy = isStarting || run.status === 'syncing'

  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{label}</h2>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
        </div>
        <button
          type="button"
          onClick={onSync}
          disabled={busy}
          className="rounded-lg bg-amber-500 px-4 py-2 font-medium text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Syncing…' : 'Sync'}
        </button>
      </div>

      <div className="mt-4 space-y-3">
        {busy ? <StatusBanner tone="info">Syncing… fetching and saving catalog data.</StatusBanner> : null}
        {run.status === 'succeeded' ? <StatusBanner tone="success">Sync completed</StatusBanner> : null}
        {run.status === 'failed' ? (
          <StatusBanner tone="error">{run.error ?? 'Sync failed.'}</StatusBanner>
        ) : null}
        {startError ? <StatusBanner tone="error">{startError}</StatusBanner> : null}
        {run.result ? <ImportResultPanel result={run.result} /> : null}
        <ImporterJobLog logs={run.logs} />
      </div>
    </article>
  )
}
