import { http } from '../../../shared/api/http'
import type { ImporterInfo, StartSyncRequest, StartSyncResponse, SyncJob, TcgplayerGroup } from '../model/types'

export async function listImporters() {
  const { data } = await http.get<ImporterInfo[]>('/importers/')
  return data
}

export async function listTcgcsvGroups() {
  const { data } = await http.get<TcgplayerGroup[]>('/importers/tcgcsv/groups')
  return data
}

export async function startSync(source: string, body?: StartSyncRequest) {
  const { data } = await http.post<StartSyncResponse>(`/importers/${source}/sync`, body ?? {})
  return data
}

export async function getJob(jobId: string) {
  const { data } = await http.get<SyncJob>(`/importers/jobs/${jobId}`)
  return data
}
