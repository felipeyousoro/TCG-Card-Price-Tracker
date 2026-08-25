export const stockKeys = {
  all: ['stock'] as const,
  holdings: (page: number) => [...stockKeys.all, 'holdings', page] as const,
  transactions: (page: number) => [...stockKeys.all, 'transactions', page] as const,
  quantities: () => [...stockKeys.all, 'quantities'] as const,
}
