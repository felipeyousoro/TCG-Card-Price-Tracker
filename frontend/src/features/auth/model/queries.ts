import { queryOptions, useQuery } from '@tanstack/react-query'

import { checkAuth } from '../api/authApi'
import { authKeys } from './keys'

export const sessionQueryOptions = queryOptions({
  queryKey: authKeys.session(),
  queryFn: checkAuth,
  staleTime: 5 * 60 * 1000,
  retry: false,
})

export function useSession() {
  return useQuery(sessionQueryOptions)
}
