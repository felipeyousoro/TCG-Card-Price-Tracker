import { Link } from 'react-router-dom'

import PageHeader from '../../../shared/ui/PageHeader'
import { settingsNav } from '../model/nav'

export default function SettingsPage() {
  return (
    <>
      <PageHeader
        title="Settings"
        description="Admin tools for this workspace. More sections will land here later."
      />
      <ul className="space-y-3">
        {settingsNav.map((item) => (
          <li key={item.path}>
            <Link
              to={item.path}
              className="block rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4 transition hover:border-amber-500/40 hover:bg-slate-900"
            >
              <span className="font-medium text-amber-400">{item.label}</span>
              <p className="mt-1 text-sm text-slate-400">{item.description}</p>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}
