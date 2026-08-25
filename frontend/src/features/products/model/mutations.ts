import { useMutation, useQueryClient } from '@tanstack/react-query'

import { createProduct } from '../api/productsApi'
import { productKeys } from './keys'
import type { ProductCreate } from './types'

export function useCreateProductMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: ProductCreate) => createProduct(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: productKeys.all })
    },
  })
}
