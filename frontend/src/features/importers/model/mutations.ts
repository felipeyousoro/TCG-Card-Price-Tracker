import { useMutation, useQueryClient } from '@tanstack/react-query'

import { startSync } from '../api/importersApi'
import { importerKeys } from './keys'
import type { SyncJob } from './types'

export function useStartSyncMutation(source: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: [...importerKeys.all, 'sync', source],
    mutationFn: () => startSync(source),
    retry: 0,
    onSuccess: (data) => {
      const queued: SyncJob = {
        id: data.job_id,
        source,
        status: 'queued',
        fetched: null,
        inserted: null,
        skipped: null,
        error: null,
        logs: [],
        created_at: new Date().toISOString(),
        started_at: null,
        finished_at: null,
      }
      queryClient.setQueryData(importerKeys.job(data.job_id), queued)
    },
  })
}
