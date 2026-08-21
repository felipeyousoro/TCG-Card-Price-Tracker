import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { catalogKeys } from '../../../shared/query/catalogKeys'
import { useStartSyncMutation } from './mutations'
import { importerKeys } from './keys'
import { jobQueryOptions } from './queries'
import { isActiveJobStatus, jobToRun, type ImporterInfo } from './types'

export function useImporterSync(importer: ImporterInfo) {
  const queryClient = useQueryClient()
  const startMutation = useStartSyncMutation(importer.source)

  const resumeJobId =
    importer.latest_job && isActiveJobStatus(importer.latest_job.status)
      ? importer.latest_job.id
      : undefined
  const jobId = startMutation.data?.job_id ?? resumeJobId

  const jobQuery = useQuery({
    ...jobQueryOptions(jobId ?? ''),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'succeeded' || status === 'failed') {
        return false
      }
      return 1500
    },
  })

  useEffect(() => {
    if (jobQuery.data?.status !== 'succeeded') {
      return
    }
    void queryClient.invalidateQueries({ queryKey: importerKeys.list() })
    void queryClient.invalidateQueries({ queryKey: catalogKeys.all })
  }, [jobQuery.data?.id, jobQuery.data?.status, queryClient])

  const job = jobQuery.data ?? importer.latest_job
  const run = jobToRun(importer.source, job)

  return {
    run,
    isStarting: startMutation.isPending,
    startError: startMutation.error,
    sync: () => startMutation.mutate(),
  }
}
