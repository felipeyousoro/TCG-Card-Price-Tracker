export const favoriteKeys = {
  all: ['favorites'] as const,
  list: (page: number) => [...favoriteKeys.all, 'list', page] as const,
  ids: () => [...favoriteKeys.all, 'ids'] as const,
}
