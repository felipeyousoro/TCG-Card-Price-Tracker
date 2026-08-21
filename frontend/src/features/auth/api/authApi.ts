import { http, setCsrfToken } from '../../../shared/api/http'
import type { AuthStatus, LoginPayload, LoginResponse } from '../model/types'

export async function login(payload: LoginPayload) {
  const { data } = await http.post<LoginResponse>('/auth/login', payload)
  setCsrfToken(data.csrf_token)
  return data
}

export async function logout() {
  await http.post('/auth/logout')
  setCsrfToken(null)
}

export async function checkAuth() {
  const { data } = await http.get<AuthStatus>('/auth/check-auth')
  return data
}
