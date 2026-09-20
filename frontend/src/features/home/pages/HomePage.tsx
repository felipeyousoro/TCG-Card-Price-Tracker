import { Link } from 'react-router-dom'

import { apiErrorMessage } from '../../../shared/api/errors'
import PageHeader from '../../../shared/ui/PageHeader'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useDashboardSeries, useDashboardSummary } from '../../dashboard/model/queries'
import { ALL_TIME_RANGE } from '../../dashboard/model/types'
import DashboardCharts from '../../dashboard/ui/DashboardCharts'
import SummaryCards from '../../dashboard/ui/SummaryCards'

export default function HomePage() {
  const summaryQuery = useDashboardSummary(ALL_TIME_RANGE)
  const seriesQuery = useDashboardSeries(ALL_TIME_RANGE)
  const empty =
    summaryQuery.data &&
    summaryQuery.data.total_invested === 0 &&
    summaryQuery.data.total_proceeds === 0 &&
    summaryQuery.data.holdings_count === 0

  return (
    <>
      <PageHeader title="Home" description="All-time cost basis and realized P&L. Market value comes later." />
      <div className="mb-6">
        <Link to="/dashboards" className="text-sm text-amber-400 hover:text-amber-300">
          Open Dashboards
        </Link>
      </div>
      {summaryQuery.isLoading ? <p className="text-slate-400">Loading P&L…</p> : null}
      {summaryQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(summaryQuery.error)}</StatusBanner> : null}
      {summaryQuery.data ? <SummaryCards summary={summaryQuery.data} compact /> : null}
      {empty ? <p className="mt-6 text-slate-400">No buys or sells recorded yet.</p> : null}
      <div className="mt-8">
        {seriesQuery.isError ? <StatusBanner tone="error">{apiErrorMessage(seriesQuery.error)}</StatusBanner> : null}
        {seriesQuery.data ? <DashboardCharts points={seriesQuery.data.points} compact /> : null}
      </div>
    </>
  )
}
