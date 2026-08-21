import { queryOptions, useQuery } from '@tanstack/react-query'

import { getJob, listImporters } from '../api/importersApi'
import { importerKeys } from './keys'

export const importersListQueryOptions = queryOptions({
  queryKey: importerKeys.list(),
  queryFn: listImporters,
})

export function jobQueryOptions(jobId: string) {
  return queryOptions({
    queryKey: importerKeys.job(jobId),
    queryFn: () => getJob(jobId),
  })
}

export function useImportersList() {
  return useQuery(importersListQueryOptions)
}
