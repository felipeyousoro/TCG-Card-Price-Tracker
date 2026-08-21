import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-slate-100">
      <div className="w-full max-w-md">
        <p className="mb-6 text-center text-lg font-semibold">TCG Card Price Tracker</p>
        <Outlet />
      </div>
    </div>
  )
}
