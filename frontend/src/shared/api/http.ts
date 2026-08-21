import axios from 'axios'

import { queryClient } from '../../app/queryClient'
import { getCookie } from '../lib/cookies'

let csrfToken: string | null = null

export function setCsrfToken(token: string | null) {
  csrfToken = token
}

export const http = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  timeout: 30_000,
})

http.interceptors.request.use((config) => {
  const method = config.method?.toLowerCase()
  if (method && !['get', 'head', 'options'].includes(method)) {
    const token = getCookie('csrf_token') ?? csrfToken
    if (token) {
      config.headers['X-CSRF-Token'] = token
    }
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const url = error.config?.url ?? ''
      if (!url.includes('/auth/login')) {
        csrfToken = null
        queryClient.clear()
        if (window.location.pathname !== '/login') {
          window.location.assign('/login')
        }
      }
    }
    return Promise.reject(error)
  },
)
