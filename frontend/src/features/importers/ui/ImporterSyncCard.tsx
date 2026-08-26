import StatusBanner from '../../../shared/ui/StatusBanner'
import type { ImporterRun, TcgplayerGroup } from '../model/types'
import ImporterJobLog from './ImporterJobLog'
import ImportResultPanel from './ImportResultPanel'

const buttonClass =
  'rounded-lg bg-amber-500 px-4 py-2 font-medium text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-60'

export default function ImporterSyncCard({
  label,
  description,
  run,
  isStarting,
  startError,
  groups,
  selectedGroupId,
  onSelectedGroupIdChange,
  onSyncSelected,
  onSyncAll,
}: {
  label: string
  description: string
  run: ImporterRun
  isStarting: boolean
  startError?: string
  groups: TcgplayerGroup[]
  selectedGroupId: string
  onSelectedGroupIdChange: (value: string) => void
  onSyncSelected: () => void
  onSyncAll: () => void
}) {
  const busy = isStarting || run.status === 'syncing'

  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{label}</h2>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only" htmlFor="tcgcsv-group">
            TCGPlayer group
          </label>
          <select
            id="tcgcsv-group"
            value={selectedGroupId}
            onChange={(event) => onSelectedGroupIdChange(event.target.value)}
            disabled={busy}
            className="max-w-xs rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200"
          >
            <option value="">Select a group</option>
            {groups.map((group) => (
              <option key={group.group_id} value={String(group.group_id)}>
                {group.name}
                {group.enabled ? '' : ' (disabled)'}
              </option>
            ))}
          </select>
          <button type="button" onClick={onSyncSelected} disabled={busy || !selectedGroupId} className={buttonClass}>
            {busy ? 'Syncing…' : 'Sync selected'}
          </button>
          <button type="button" onClick={onSyncAll} disabled={busy} className={buttonClass}>
            {busy ? 'Syncing…' : 'Sync all'}
          </button>
        </div>
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
