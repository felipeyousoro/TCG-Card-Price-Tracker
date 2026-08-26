import { queryOptions, useQuery } from '@tanstack/react-query'

import { getJob, listImporters, listTcgcsvGroups } from '../api/importersApi'
import { importerKeys } from './keys'

export const importersListQueryOptions = queryOptions({
  queryKey: importerKeys.list(),
  queryFn: listImporters,
})

export const tcgcsvGroupsQueryOptions = queryOptions({
  queryKey: importerKeys.groups(),
  queryFn: listTcgcsvGroups,
})

export function jobQueryOptions(jobId: string) {
  return queryOptions({
    queryKey: importerKeys.job(jobId),
    queryFn: () => getJob(jobId),
  })
}

export function useTcgcsvGroups() {
  return useQuery(tcgcsvGroupsQueryOptions)
}

export function useImportersList() {
  return useQuery(importersListQueryOptions)
}
