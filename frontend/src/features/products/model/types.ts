export type ProductCategory = 'box' | 'case' | 'pack' | 'starter_deck' | 'other'

export const PRODUCT_CATEGORIES: { value: ProductCategory; label: string }[] = [
  { value: 'box', label: 'Booster box' },
  { value: 'case', label: 'Case' },
  { value: 'pack', label: 'Pack' },
  { value: 'starter_deck', label: 'Starter deck' },
  { value: 'other', label: 'Other' },
]

export type ProductListItem = {
  id: number
  name: string
  category: ProductCategory
  set_name: string | null
  image_url: string | null
}

export type ProductRead = ProductListItem & {
  created_by_user_id: number | null
  created_at: string
  updated_at: string | null
}

export type ProductCreate = {
  name: string
  category: ProductCategory
  set_name?: string | null
  image_url?: string | null
}

export type PaginatedProducts = {
  data: ProductListItem[]
  total_count: number
  has_more: boolean
  page: number | null
  items_per_page: number | null
}
