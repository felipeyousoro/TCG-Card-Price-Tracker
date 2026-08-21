export type SyncJobStatus = 'queued' | 'running' | 'succeeded' | 'failed'

export type SyncJobLogLevel = 'info' | 'warning' | 'error'

export type SyncJobLogEntry = {
  at: string
  level: SyncJobLogLevel
  message: string
}

export type SyncJob = {
  id: string
  source: string
  status: SyncJobStatus
  fetched: number | null
  inserted: number | null
  skipped: number | null
  error: string | null
  logs: SyncJobLogEntry[]
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export type ImporterInfo = {
  source: string
  label: string
  description: string
  latest_job: SyncJob | null
}

export type StartSyncResponse = {
  job_id: string
}

export type ImportResultCounts = {
  fetched: number
  inserted: number
  skipped: number
}

export type ImporterRun = {
  source: string
  jobId?: string
  status: 'idle' | 'syncing' | 'succeeded' | 'failed'
  result?: ImportResultCounts
  error?: string
  logs: SyncJobLogEntry[]
}

export function isActiveJobStatus(status: SyncJobStatus) {
  return status === 'queued' || status === 'running'
}

export function jobToRun(source: string, job: SyncJob | null | undefined): ImporterRun {
  if (!job) {
    return { source, status: 'idle', logs: [] }
  }

  const status: ImporterRun['status'] = isActiveJobStatus(job.status)
    ? 'syncing'
    : job.status === 'succeeded'
      ? 'succeeded'
      : job.status === 'failed'
        ? 'failed'
        : 'idle'

  const result =
    job.status === 'succeeded' && job.fetched != null && job.inserted != null && job.skipped != null
      ? { fetched: job.fetched, inserted: job.inserted, skipped: job.skipped }
      : undefined

  return {
    source,
    jobId: job.id,
    status,
    result,
    error: job.error ?? undefined,
    logs: job.logs ?? [],
  }
}
