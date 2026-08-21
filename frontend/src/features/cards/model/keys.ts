import type { OptcgCardListParams } from './types'

export const cardKeys = {
  all: ['cards'] as const,
  optcg: () => [...cardKeys.all, 'optcg'] as const,
  filters: () => [...cardKeys.optcg(), 'filters'] as const,
  list: (params: OptcgCardListParams) => [...cardKeys.optcg(), 'list', params] as const,
}
