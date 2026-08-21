export type SessionUser = {
  id: number
  username: string
}

export type AuthStatus = {
  authenticated: boolean
  message?: string
  user?: SessionUser
  session?: {
    created_at: string | null
    last_activity: string | null
  }
}

export type LoginPayload = {
  username: string
  password: string
}

export type LoginResponse = {
  csrf_token: string
}
