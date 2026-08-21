import { Navigate, Outlet } from 'react-router-dom'

import { useSession } from './model/queries'

export default function RequireAuth() {
  const { data, isLoading } = useSession()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
        Checking session…
      </div>
    )
  }

  if (!data?.authenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
