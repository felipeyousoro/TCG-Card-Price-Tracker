import { useEffect, useState } from 'react'
import { getOnepieceCards } from '../api/client'
import type { OnePieceCard } from '../types/onepiece'

export default function Home() {
  const [cards, setCards] = useState<OnePieceCard[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getOnepieceCards({ rarity: 'SR', limit: 100 })
      .then((data) => {
        setCards(data.items)
        setTotal(data.total)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load cards')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
        Loading SR cards…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-red-400">
        {error}
      </div>
    )
  }

  return (
    <>
      <header className="border-b border-slate-800 px-6 py-8">
        <h1 className="text-3xl font-bold tracking-tight">SR Cards</h1>
        <p className="mt-2 text-slate-400">
          Showing {cards.length} of {total} SR cards
        </p>
      </header>

      <main className="px-6 py-8">
        {cards.length === 0 ? (
          <p className="text-slate-400">No SR cards found.</p>
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {cards.map((card) => (
              <li
                key={card.id}
                className="rounded-lg border border-slate-800 bg-slate-900 p-4 transition hover:border-amber-500/50"
              >
                <p className="font-mono text-sm text-amber-400">{card.code}</p>
                <p className="mt-1 text-lg font-semibold">{card.rarity}</p>
                <p className="mt-2 text-sm text-slate-400">{card.collection}</p>
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  )
}
