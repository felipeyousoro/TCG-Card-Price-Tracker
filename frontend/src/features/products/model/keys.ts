export const productKeys = {
  all: ['products'] as const,
  list: (q: string) => [...productKeys.all, 'list', q] as const,
}
