export const importerKeys = {
  all: ['importers'] as const,
  list: () => [...importerKeys.all, 'list'] as const,
  jobs: () => [...importerKeys.all, 'jobs'] as const,
  job: (jobId: string) => [...importerKeys.jobs(), jobId] as const,
}
