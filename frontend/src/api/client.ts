import axios from 'axios'
import type {
  Collection,
  OnePieceCard,
  PaginatedResponse,
  ScrapeCollectionOption,
  ScrapeResponse,
} from '../types/onepiece'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

export interface GetCardsParams {
  collection?: string
  rarity?: string
  page?: number
  limit?: number
}

export async function getOnepieceCards(params: GetCardsParams = {}) {
  const { data } = await api.get<PaginatedResponse<OnePieceCard>>('/ligaonepiece/get_onepiece_cards', {
    params,
  })
  return data
}

export async function getOnepieceCollections(page = 1, limit = 50) {
  const { data } = await api.get<PaginatedResponse<Collection>>('/ligaonepiece/get_onepiece_collections', {
    params: { page, limit },
  })
  return data
}

export async function getScrapeCollections() {
  const { data } = await api.get<{ items: ScrapeCollectionOption[] }>('/ligaonepiece/get_scrape_collections')
  return data
}

export async function scrapeCollection(collection: string) {
  const { data } = await api.post<ScrapeResponse>('/ligaonepiece/scrape-collection', { collection })
  return data
}
