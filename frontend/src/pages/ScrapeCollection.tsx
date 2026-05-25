import { useEffect, useState } from 'react'
import { getScrapeCollections, scrapeCollection } from '../api/client'
import type { ScrapeCollectionOption } from '../types/onepiece'

type ScrapeStatus = 'idle' | 'loading' | 'success' | 'error'

export default function ScrapeCollectionPage() {
  const [collections, setCollections] = useState<ScrapeCollectionOption[]>([])
  const [selected, setSelected] = useState('')
  const [loadingList, setLoadingList] = useState(true)
  const [status, setStatus] = useState<ScrapeStatus>('idle')
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    getScrapeCollections()
      .then((data) => {
        setCollections(data.items)
        if (data.items.length > 0) {
          setSelected(data.items[0].collection)
        }
      })
      .catch((err) => {
        setMessage(err instanceof Error ? err.message : 'Failed to load collections')
        setStatus('error')
      })
      .finally(() => setLoadingList(false))
  }, [])

  async function handleScrape() {
    if (!selected) return

    setStatus('loading')
    setMessage(null)

    try {
      const result = await scrapeCollection(selected)
      setMessage(result.message)
      setStatus('success')
    } catch (err) {
      const detail =
        axiosErrorMessage(err) ?? (err instanceof Error ? err.message : 'Scrape failed')
      setMessage(detail)
      setStatus('error')
    }
  }

  if (loadingList) {
    return (
      <div className="flex min-h-[calc(100vh-57px)] items-center justify-center text-slate-300">
        Loading collections…
      </div>
    )
  }

  return (
    <div className="px-6 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Scrape Collection</h1>
        <p className="mt-2 text-slate-400">
          Pick a Liga One Piece edition and import all its cards into the database.
        </p>
      </header>

      <div className="max-w-xl space-y-6">
        <label className="block">
          <span className="mb-2 block text-sm text-slate-400">Collection</span>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            disabled={status === 'loading'}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-amber-500 disabled:opacity-50"
          >
            {collections.map((item) => (
              <option key={item.collection} value={item.collection}>
                {item.collection}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={handleScrape}
          disabled={!selected || status === 'loading'}
          className="flex items-center gap-3 rounded-lg bg-amber-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {status === 'loading' && (
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
          )}
          {status === 'loading' ? 'Scraping…' : 'Scrape cards'}
        </button>

        {status === 'loading' && (
          <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-amber-300">
            Scraping <strong>{selected}</strong> — this may take a minute…
          </div>
        )}

        {status === 'success' && message && (
          <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-emerald-300">
            {message}
          </div>
        )}

        {status === 'error' && message && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-300">
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

function axiosErrorMessage(err: unknown): string | null {
  if (typeof err === 'object' && err !== null && 'response' in err) {
    const response = (err as { response?: { data?: { detail?: string } } }).response
    if (typeof response?.data?.detail === 'string') {
      return response.data.detail
    }
  }
  return null
}
