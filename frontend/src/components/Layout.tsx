import { Link, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="flex items-center gap-6">
          <span className="text-lg font-semibold">One Piece Card Tracker</span>
          <Link to="/" className="text-slate-400 transition hover:text-amber-400">
            Cards
          </Link>
          <Link to="/scrape" className="text-slate-400 transition hover:text-amber-400">
            Scrape Collection
          </Link>
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
