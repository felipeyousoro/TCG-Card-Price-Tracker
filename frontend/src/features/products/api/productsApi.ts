import { http } from '../../../shared/api/http'
import type { PaginatedProducts, ProductCreate, ProductRead } from '../model/types'

export async function searchProducts(q: string, page = 1) {
  const { data } = await http.get<PaginatedProducts>('/products', {
    params: { q: q || undefined, page, items_per_page: 10 },
  })
  return data
}

export async function createProduct(payload: ProductCreate) {
  const { data } = await http.post<ProductRead>('/products', payload)
  return data
}
