import { http } from '../../../shared/api/http'
import type { ImporterInfo, StartSyncResponse, SyncJob } from '../model/types'

export async function listImporters() {
  const { data } = await http.get<ImporterInfo[]>('/importers/')
  return data
}

export async function startSync(source: string) {
  const { data } = await http.post<StartSyncResponse>(`/importers/${source}/sync`)
  return data
}

export async function getJob(jobId: string) {
  const { data } = await http.get<SyncJob>(`/importers/jobs/${jobId}`)
  return data
}
