# TCG Card Price Tracker — Next Steps Implementation Plan

Priority order: **Phase 0 (multi-game catalog foundation) → Phase 1 (Stock incl. Buy) → Phase 2 (Favorites) → Phase 3 (Sales/Buy Dashboard, average-cost P&L) → Phase 4 (Price import + watching/history, last)**.

This is a personal stock-management/sales tracker, not a marketplace — there's no user-to-user trading. Every buy/sell is between the user and an outside party (a store, an online marketplace, etc.); the app just records it.

## Where the app stands today

- **Backend**: FastAPI, modular `api/modules/<domain>/{models,schemas,crud,service,routes,dependencies}`, SQLAlchemy 2.0 async (dataclass-style models, `UUIDMixin`/`TimestampMixin`/`SoftDeleteMixin`), FastCRUD for list/paginate, Alembic migrations, session-based auth (`CurrentUserDep` → `{"id": int, ...}`). Only one catalog exists today: `optcg_card` (One Piece TCG), with **no price field at all** — pricing is a brand-new domain.
- **Importers**: a clean `OptcgImporter` protocol (`base.py`) + `registry.py` (source → importer) + per-source folder (`client/mapper/importer/routes/schemas`) + a generic background job runner (`importers/jobs/*`) that the settings UI already polls. Reusable for price importers later.
- **Frontend**: React 19 + TanStack Query + React Router, feature folders (`model/{keys,queries,mutations,types}`, `ui/`, `api/`, `pages/`), shared `PageHeader`/`StatusBanner`, `AppShell` layout, a `cardGames` config (currently just OPTCG) and a `settingsNav` array that auto-lists importer cards.
- **Multi-game plans**: Pokémon and Magic are coming later, which shapes Phase 0 below.
- **Other gaps**: no test suite in `api/`, no charting library in `frontend/package.json` (needed by Phase 3/4), no card detail page (needed by Phase 4).

---

## Phase 0 — Multi-game catalog foundation (do this first)

**Goal**: decouple stock, favorites, and price tracking from any single game's card table, so adding Pokémon/Magic later means "add a new detail table + importer," not "touch four other domains."

### Design: base identity table + per-game detail table
Not Postgres native `INHERITS` (unique constraints/FKs don't propagate cleanly to child tables, and SQLAlchemy support is awkward) — plain FK composition instead:

| Table | Purpose | Key columns |
|---|---|---|
| `card` (new, shared) | Universal identity every game shares | `id` (int pk), `game` (enum: `optcg`, `mtg`, `pokemon`, …), `name`, `set_name`, `set_code`, `card_number`, `rarity`, `card_type`, `image_url`, timestamps |
| `optcg_card` (narrowed) | OPTCG-only fields | `card_id` (FK `card.id`, unique/1:1), `card_text`, `card_color`, `life`, `card_cost`, `card_power`, `sub_types`, `counter_amount`, `attribute`, `card_image_id`, `date_scraped` |
| `mtg_card` / `pokemon_card` (future) | Same pattern, added only when that game ships | `card_id` FK + that game's own columns |

Cross-cutting tables (`stock_transaction`, `favorite`, `card_price`, …) FK to **`card.id`**, never to a game-specific table — that target never changes as games are added. Confirmed: the proposed base schema (`name`, `set_name`, `set_code`, `card_number`, `rarity`, `card_type`, `image_url`) covers Magic and Pokémon's universal fields fine; game-specific stuff (mana cost, HP, weakness, etc.) lives in each game's own detail table.

### Migration & backfill
One Alembic migration: create `card`, backfill by copying the shared columns out of every existing `optcg_card` row, add `card_id` to `optcg_card`, drop the now-duplicated columns from `optcg_card`.

### Backend changes
- New `api/modules/cards/` — owns the `card` base table, generic list/filter/detail endpoints that work across every game.
- `api/modules/optcg/` narrows to the `optcg_card` detail table + importer/mapper (now writes a `card` row **and** an `optcg_card` detail row per import, in one transaction).
- `OptcgCatalogService.list_paginated` becomes a join across `card` + `optcg_card` — same filters (`color`, `rarity`, `set_name`) still work.

### Frontend impact
Minimal by design: if `/optcg/cards` keeps returning the same merged shape, `CardTile`, `CardFilters`, and `OptcgCardsPage` don't need to change at all.

---

## Phase 1 — Stock (holdings) + Buy history

**Goal**: users can record what they own and what they paid, including bulk backfill, with a proper order/line structure so "cards bought in one trip" stay grouped together.

### Data model (Alembic migration)

**`transaction`** (header — one buy or sell *event*, e.g. one store visit or one online order):
| Column | Notes |
|---|---|
| `id` | uuid pk |
| `user_id` | FK `user.id` |
| `transaction_type` | enum `buy` / `sell` |
| `transaction_date` | date |
| `notes?` | e.g. "Local game store", "eBay order #4471" |
| `created_at` | |

**`stock_transaction`** (line item — one card or product within a transaction):
| Column | Notes |
|---|---|
| `id` | uuid pk |
| `transaction_id` | FK `transaction.id` |
| `user_id` | FK `user.id`, denormalized from the header for cheap per-user queries (matches how `SyncJob` already denormalizes `created_by_user_id` rather than always joining) |
| `card_id?` | FK **`card.id`** |
| `product_id?` | FK `product.id` — `CHECK` exactly one of `card_id`/`product_id` set |
| `quantity` | int |
| `unit_price` | numeric |
| `line_total` | numeric, computed |
| `notes?` | optional per-line note (e.g. condition) |

**`user_card_stock`** / **`user_product_stock`**: unchanged from before — aggregate `(user_id, card_id/product_id) → quantity, avg_unit_cost`, maintained by the service layer whenever a line is inserted.

**`product`**: **shared catalog**, same spirit as `card` — sealed products are reference data, and multiple users buying the same "One Piece OP-10 Booster Box" should point at the same catalog row, not each create their own copy. `id`, `name`, `category` enum (box/case/pack/starter_deck/other), `set_name?`, `image_url?`, `created_by_user_id?` (attribution only, doesn't gate visibility — any user can browse and buy against any entry), `created_at`. No importer populates this (unlike `card`), so it's user-contributed; no hard uniqueness constraint at the DB level since near-duplicate names ("OP-10 Booster Box" vs "One Piece OP10 booster box") shouldn't be silently rejected — dedup is handled at the UX layer instead (see `ProductPicker` below).

### Backend
- `api/modules/stock/` owns `Transaction`, `StockTransaction`, `UserCardStock`, `UserProductStock` — they're tightly coupled, no reason to split into separate modules.
  - `enums.py`: `ItemType`, `TransactionType`.
  - `service.py`:
    - `record_buy(user_id, transaction_date, lines: list[LineIn], notes=None)` — creates one `transaction` header + N `stock_transaction` lines + upserts aggregate stock, all in one DB transaction. A single quick-buy from a card tile is just this called with one line.
    - `list_holdings(user_id, ...)` — paginated, joined to `card`/`optcg_card`/`product`.
    - `list_transactions(user_id, filters)` — order history (header + its lines).
    - `bulk_import_buys(user_id, rows)` — see mass-import format below.
  - `routes.py`: `POST /stock/cards/{card_id}/buy` (single-line convenience), `POST /stock/transactions` (multi-line, for a future "log an order" screen), `GET /stock`, `GET /stock/transactions`, `POST /stock/transactions/import`, `DELETE /stock/transactions/{id}`.

### Mass-import format for buy history
CSV needs a grouping column now so multiple rows from the same real-world order become one `transaction` header instead of N separate ones:

```
order_ref, date, card_set_id, product_name, quantity, unit_price, notes
order-1, 2026-03-01, OP01-001, , 3, 4.50,
order-1, 2026-03-01, OP01-045, , 1, 12.00,
order-2, 2026-03-01, , One Piece OP-10 Booster Box, 1, 95.00, opened at release
```
Rows sharing an `order_ref` become lines under one `transaction`; a blank `order_ref` becomes its own single-line transaction. Response follows the existing `ImportResult`-style shape (`fetched`/`inserted`/`skipped` + per-row errors) so the UI can reuse `ImportResultPanel`.

### Frontend
- `features/stock/` — `model/{keys,queries,mutations,types}.ts`, `api/stockApi.ts`, `ui/BuyDialog.tsx`, `ui/HoldingsTable.tsx`, `ui/ImportBuyHistoryForm.tsx`.
- `features/products/` — `ProductForm.tsx`, `ProductPicker.tsx` (search-or-create against the shared catalog — search first, only fall through to "create new" if nothing matches, to keep duplicate entries down).
- Extend `CardTile` with an owned-quantity badge + "Buy" button opening `BuyDialog`.
- New pages: `/stock` (holdings + transaction history tabs), `/stock/import`.

---

## Phase 2 — Favorites

**Goal**: quick "star" a card (and product) for later.

### Backend
- `api/modules/favorites/`: `favorite` table — `id`, `user_id`, `card_id?` FK **`card.id`**, `product_id?` FK `product.id` (same exactly-one-set constraint as stock), `created_at`, unique per (`user_id`,`card_id`) / (`user_id`,`product_id`).
- Routes: `POST /favorites`, `DELETE /favorites/{id}`, `GET /favorites`.

### Frontend
- `features/favorites/` (mirrors `stock`).
- Heart-icon toggle on `CardTile` with optimistic update.
- `FavoritesPage` (`/favorites`) reusing the existing grid + `PaginationBar`.

Works identically for every future game since it FKs to the base `card`/`product` tables. This table is also the natural home for the Phase 4 price-alert flag (`price_alert_threshold`), added via its own migration when Phase 4 needs it.

---

## Phase 3 — Sales / Buy Dashboard (Average Cost)

**Goal**: a real P&L view, using the recorded average paid cost at the moment of sale and recorded sale prices (no live market value until Phase 4).

### Average-cost basis tracking
Sales use the aggregate `avg_unit_cost` for the user's holding at the exact time the sale is recorded. This value must be snapshotted onto the sell line because `avg_unit_cost` can change later when additional buys are recorded. Historical P&L must never be affected by future purchases.

No FIFO lot-consumption table is needed. A sell does not select or consume individual buy lots; instead, it captures the current weighted-average paid price as the cost basis for that sale.

Extend **`stock_transaction`** with:
| Column | Notes |
|---|---|
| `avg_unit_cost_at_sale` | numeric, snapshot of the user's current `avg_unit_cost` for the card/product immediately before recording the sale |
| `realized_gain` | numeric, `(unit_price - avg_unit_cost_at_sale) * quantity` |

`record_sell(...)` service logic: validate available stock → read the current aggregate `avg_unit_cost` for that user+card/product before changing the holding → store that value as `avg_unit_cost_at_sale` on the sell line → calculate and store `realized_gain` → insert the sell transaction/line → decrement the aggregate stock row.

The stored `avg_unit_cost_at_sale` is the historical cost basis. It must not be recalculated from current holdings or future purchases when reporting past sales.

### Backend
- Extend `stock` service with `record_sell(...)` per above.
- Reporting endpoints:
  - `GET /dashboard/summary` — total invested, total realized from sales, realized P&L (`SUM(stock_transaction.realized_gain)` for sell lines), current holdings count & remaining cost basis.
  - `GET /dashboard/transactions` — unified buy+sell feed (headers + lines), date/card filters.
  - `GET /dashboard/by-card` — top holdings/best-and-worst realized gains by card.

### Frontend
- "Sell" action alongside "Buy" on the holdings page.
- `features/dashboard/` → `DashboardPage` (`/dashboard`): summary cards, transaction table, spend-over-time chart. **Needs a charting library added** (e.g. Recharts) — none exists in `package.json` today.

---

## Phase 4 — Price import + price watching/history (last)

**Goal**: pull external prices, let users watch cards, surface spikes.

### Data model
- `card_price` (time series): `id`, `card_id` FK **`card.id`**, `source` (`tcgplayer`/`ligaonepiece`), `scraped_at`, `price`, `price_type`, `currency`. Indexed on (`card_id`,`source`,`scraped_at`).
- Optional `price_spike_event` for a fast "trending" feed instead of computing deltas on every read.
- `card_external_id` mapping table per source if names don't line up cleanly, FK'd to `card.id` (works the same for every future game).

### Backend
- `TCGPlayer` importer: real API — client + mapper + importer following the existing `OptcgImporter` protocol shape, needs an API key in `core/config/settings.py`.
- `Liga One Piece` importer: **confirmed scraper**, not an API. Needs its own care beyond the normal importer shape:
  - Respect robots.txt and rate-limit requests (delay + a real user agent).
  - Check at build time whether the pricing pages are server-rendered HTML (plain `httpx` + `selectolax`/`BeautifulSoup` parsing is enough) or JS-rendered (would need Playwright — heavier dependency, worth confirming before committing to the approach).
  - More fragile than an API integration by nature — plan for markup-change monitoring/alerting on the scheduled job, since it will silently break when the site changes.
- Reuse the existing importer registry + job runner (`jobs/runner.py` currently assumes the catalog-import shape `import_all_sets` — generalize it or add a parallel `price_jobs` runner).
- New routes: `GET /prices/cards/{id}/history`, `GET /prices/spikes`.
- Price watching: nullable `price_alert_threshold` column on the Phase 2 `favorite` table.

### Frontend
- A proper **CardDetailPage** (doesn't exist yet) to host the price chart, watch toggle, current price.
- Spike/"trending" feed, likely on the Dashboard or Home page.
- Importer settings page picks up both new sources automatically via the existing `/importers` list.

---

## Rough sequencing

```
Phase 0 (card/product base tables)
        │  unblocks every FK below, for every future game
        ▼
Phase 1 (Stock+Buy, transaction header/lines)  →  Phase 2 (Favorites)  →  Phase 3 (Dashboard, average-cost P&L)  →  Phase 4 (Price import/watch/history)
```

## Remaining open items
1. CSV `order_ref` grouping (Phase 1 import): free-text, user-supplied, or should the UI generate one automatically per upload session unless the user opts to group manually?
2. `product` dedup across the shared catalog: `ProductPicker`'s search-first UX helps, but exact-match search alone will still miss near-duplicates ("OP-10 Booster Box" vs "One Piece OP10 booster box"). Worth deciding whether to add fuzzy/trigram search (Postgres `pg_trgm`) up front or start simple and revisit once real duplicate entries show up.
3. Liga One Piece: confirm server-rendered vs. JS-rendered before starting that importer, to know whether Playwright is needed.
