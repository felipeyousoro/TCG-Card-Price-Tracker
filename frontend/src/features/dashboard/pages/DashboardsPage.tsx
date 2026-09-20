import { useMemo, useState } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { todayISODate } from '../../stock/model/format'
import { useDashboardByItem, useDashboardSeries, useDashboardSummary } from '../model/queries'
import { daysAgoInclusive, type DatePreset } from '../model/range'
import DashboardCharts from '../ui/DashboardCharts'
import DateRangeFilters, { activeRange } from '../ui/DateRangeFilters'
import RankingTables from '../ui/RankingTables'
import SummaryCards from '../ui/SummaryCards'

export default function DashboardsPage() {
  const [preset, setPreset] = useState<DatePreset>('30')
  const [customFrom, setCustomFrom] = useState(daysAgoInclusive(30))
  const [customTo, setCustomTo] = useState(todayISODate())
  const range = useMemo(() => activeRange(preset, customFrom, customTo), [preset, customFrom, customTo])
  const summaryQuery = useDashboardSummary(range)
  const seriesQuery = useDashboardSeries(range)
  const byItemQuery = useDashboardByItem(range)

  const hasActivity =
    (summaryQuery.data?.total_invested ?? 0) !== 0 || (summaryQuery.data?.total_proceeds ?? 0) !== 0

  return (
    <>
      <PageHeader
        title="Dashboards"
        description="Spend, realized P&L, and rankings for a date range. Holdings cost is always current."
      />
      <DateRangeFilters
        preset={preset}
        customFrom={customFrom}
        customTo={customTo}
        onPreset={setPreset}
        onCustomChange={(next) => {
          setPreset('custom')
          setCustomFrom(next.date_from)
          setCustomTo(next.date_to)
        }}
      />
      {summaryQuery.isLoading ? <p className="text-slate-400">Loading summary…</p> : null}
      {summaryQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(summaryQuery.error)}</StatusBanner> : null}
      {summaryQuery.data ? <SummaryCards summary={summaryQuery.data} /> : null}
      {summaryQuery.data && !hasActivity ? (
        <p className="mt-6 text-slate-400">No buys or sells in this range.</p>
      ) : null}

      <div className="mt-8 space-y-8">
        {seriesQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(seriesQuery.error)}</StatusBanner> : null}
        {seriesQuery.data ? <DashboardCharts points={seriesQuery.data.points} /> : null}
        {byItemQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(byItemQuery.error)}</StatusBanner> : null}
        {byItemQuery.data ? <RankingTables byItem={byItemQuery.data} /> : null}
      </div>
    </>
  )
}
