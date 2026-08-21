import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { checkAuth, login, logout } from '../api/authApi'
import { authKeys } from './keys'

export function useLoginMutation() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: login,
    onSuccess: async () => {
      const session = await checkAuth()
      queryClient.setQueryData(authKeys.session(), session)
      void navigate('/', { replace: true })
    },
  })
}

export function useLogoutMutation() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: logout,
    onSettled: () => {
      queryClient.removeQueries({ queryKey: authKeys.all })
      void navigate('/login', { replace: true })
    },
  })
}
