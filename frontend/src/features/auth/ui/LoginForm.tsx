import { useState, type FormEvent } from 'react'

import { apiErrorMessage } from '../../../shared/api/errors'
import StatusBanner from '../../../shared/ui/StatusBanner'
import { useLoginMutation } from '../model/mutations'

export default function LoginForm() {
  const loginMutation = useLoginMutation()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try {
      await loginMutation.mutateAsync({ username, password })
    } catch {
      // Error is rendered from mutation state.
    }
  }

  return (
    <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4">
      <label className="block">
        <span className="mb-1 block text-sm text-slate-300">Username</span>
        <input
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-amber-400"
        />
      </label>
      <label className="block">
        <span className="mb-1 block text-sm text-slate-300">Password</span>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-amber-400"
        />
      </label>
      {loginMutation.isError ? (
        <StatusBanner tone="error">{apiErrorMessage(loginMutation.error)}</StatusBanner>
      ) : null}
      <button
        type="submit"
        disabled={loginMutation.isPending}
        className="w-full rounded-lg bg-amber-500 px-4 py-2 font-medium text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
      </button>
    </form>
  )
}
