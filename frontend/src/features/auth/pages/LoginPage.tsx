import { Navigate } from 'react-router-dom'

import LoginForm from '../ui/LoginForm'
import { useSession } from '../model/queries'

export default function LoginPage() {
  const { data, isLoading } = useSession()

  if (isLoading) {
    return <p className="text-center text-slate-400">Checking session…</p>
  }

  if (data?.authenticated) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-8">
      <h1 className="mb-2 text-2xl font-semibold">Admin sign in</h1>
      <p className="mb-6 text-sm text-slate-400">Use the local admin account to open the shell.</p>
      <LoginForm />
    </div>
  )
}
