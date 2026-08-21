import { Link } from 'react-router-dom'

import PageHeader from '../../../shared/ui/PageHeader'
import { cardGames } from '../model/games'

export default function CardGamesPage() {
  return (
    <>
      <PageHeader title="Cards" description="Choose a card game to browse its catalog." />
      <ul className="space-y-3">
        {cardGames.map((game) => (
          <li key={game.slug}>
            <Link
              to={game.path}
              className="block rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4 transition hover:border-amber-500/40 hover:bg-slate-900"
            >
              <span className="font-medium text-amber-400">{game.label}</span>
              <p className="mt-1 text-sm text-slate-400">{game.description}</p>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}
