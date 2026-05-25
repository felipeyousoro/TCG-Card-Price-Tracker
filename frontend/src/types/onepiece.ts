export interface OnePieceCard {
  id: number
  code: string
  rarity: string
  collection: string
}

export interface Collection {
  id: number
  name: string
}

export interface ScrapeCollectionOption {
  collection: string
  url: string
}

export interface ScrapeResponse {
  status: string
  message: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}
