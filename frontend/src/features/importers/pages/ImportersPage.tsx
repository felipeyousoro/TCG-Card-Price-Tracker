import { useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useImportersList, useTcgcsvGroups } from '../model/queries'
import { useImporterSync } from '../model/useImporterSync'
import type { ImporterInfo } from '../model/types'
import ImporterSyncCard from '../ui/ImporterSyncCard'

function ImporterCardContainer({ importer }: { importer: ImporterInfo }) {
  const { run, isStarting, startError, sync } = useImporterSync(importer)
  const groupsQuery = useTcgcsvGroups()
  const [selectedGroupId, setSelectedGroupId] = useState('')

  return (
    <ImporterSyncCard
      label={importer.label}
      description={importer.description}
      run={run}
      isStarting={isStarting}
      startError={startError ? apiErrorMessage(startError) : undefined}
      groups={groupsQuery.data ?? []}
      selectedGroupId={selectedGroupId}
      onSelectedGroupIdChange={setSelectedGroupId}
      onSyncSelected={() => {
        const groupId = Number(selectedGroupId)
        if (!Number.isInteger(groupId) || groupId <= 0) {
          return
        }
        sync({ group_ids: [groupId] })
      }}
      onSyncAll={() => sync()}
    />
  )
}

export default function ImportersPage() {
  const { data, isLoading, isError, error } = useImportersList()

  return (
    <>
      <PageHeader
        title="Catalog importers"
        description="Queue a background sync. The page polls job status until it finishes."
      />
      {isLoading ? <p className="text-slate-400">Loading importers…</p> : null}
      {isError ? <StatusBanner tone="error">{apiErrorMessage(error)}</StatusBanner> : null}
      {data ? (
        <div className="space-y-4">
          {data.map((importer) => (
            <ImporterCardContainer key={importer.source} importer={importer} />
          ))}
        </div>
      ) : null}
    </>
  )
}
