import type { ImportResultCounts } from '../model/types'

export default function ImportResultPanel({ result }: { result: ImportResultCounts }) {
  return (
    <dl className="grid grid-cols-3 gap-4 text-sm">
      <div>
        <dt className="text-slate-400">Fetched</dt>
        <dd className="text-lg font-semibold text-slate-100">{result.fetched}</dd>
      </div>
      <div>
        <dt className="text-slate-400">Inserted</dt>
        <dd className="text-lg font-semibold text-slate-100">{result.inserted}</dd>
      </div>
      <div>
        <dt className="text-slate-400">Skipped</dt>
        <dd className="text-lg font-semibold text-slate-100">{result.skipped}</dd>
      </div>
    </dl>
  )
}
