import { NavLink, Outlet } from 'react-router-dom'

import { useLogoutMutation } from '../features/auth/model/mutations'
import { useSession } from '../features/auth/model/queries'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'text-amber-400' : 'text-slate-400 transition hover:text-amber-400'

export default function AppShell() {
  const { data } = useSession()
  const logoutMutation = useLogoutMutation()
  const username = data?.user?.username

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <span className="text-lg font-semibold">TCG Card Price Tracker</span>
            <NavLink to="/" end className={linkClass}>
              Home
            </NavLink>
            <NavLink to="/cards" className={linkClass}>
              Cards
            </NavLink>
            <NavLink to="/settings" className={linkClass}>
              Settings
            </NavLink>
          </div>
          <div className="flex items-center gap-4 text-sm">
            {username ? <span className="text-slate-400">{username}</span> : null}
            <button
              type="button"
              onClick={() => logoutMutation.mutate()}
              disabled={logoutMutation.isPending}
              className="text-slate-400 transition hover:text-amber-400 disabled:opacity-60"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  )
}
