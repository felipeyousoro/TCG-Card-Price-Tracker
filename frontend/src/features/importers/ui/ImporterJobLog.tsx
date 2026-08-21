import { useEffect, useRef } from 'react'

import type { SyncJobLogEntry } from '../model/types'

const levelClass: Record<SyncJobLogEntry['level'], string> = {
  info: 'text-slate-300',
  warning: 'text-amber-300',
  error: 'text-red-300',
}

function formatLogTime(at: string) {
  const date = new Date(at)
  if (Number.isNaN(date.getTime())) {
    return at
  }
  return date.toLocaleTimeString()
}

export default function ImporterJobLog({ logs }: { logs: SyncJobLogEntry[] }) {
  const scrollerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollerRef.current
    if (!el) {
      return
    }
    el.scrollTop = el.scrollHeight
  }, [logs])

  if (logs.length === 0) {
    return null
  }

  return (
    <div>
      <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Job log</h3>
      <div
        ref={scrollerRef}
        className="max-h-56 overflow-auto rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs leading-5"
      >
        {logs.map((entry, index) => (
          <div key={`${entry.at}-${index}`} className={levelClass[entry.level]}>
            <span className="text-slate-500">{formatLogTime(entry.at)}</span> {entry.message}
          </div>
        ))}
      </div>
    </div>
  )
}
