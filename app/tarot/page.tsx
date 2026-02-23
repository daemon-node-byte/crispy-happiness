'use client'

import Image from 'next/image'
import { useEffect, useMemo, useState } from 'react'

import { getTarotCard, listTarotCards } from '@/app/lib/api-client'
import { TarotCard } from '@/app/lib/types'

export default function TarotGalleryPage() {
  const [cards, setCards] = useState<TarotCard[]>([])
  const [selectedCard, setSelectedCard] = useState<TarotCard | null>(null)
  const [arcana, setArcana] = useState('')
  const [suit, setSuit] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    void loadCards()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadCards() {
    setLoading(true)
    const response = await listTarotCards()
    if (response.error || !response.data) {
      setErrorMessage(response.error?.message ?? 'Unable to load cards')
      setLoading(false)
      return
    }
    setCards(response.data.cards)
    setSelectedCard(response.data.cards[0] ?? null)
    setLoading(false)
  }

  async function applyFilters(event: React.FormEvent) {
    event.preventDefault()
    setLoading(true)
    const response = await listTarotCards({ arcana: arcana || undefined, suit: suit || undefined, search: search || undefined })
    if (response.error || !response.data) {
      setErrorMessage(response.error?.message ?? 'Unable to filter cards')
      setLoading(false)
      return
    }
    setCards(response.data.cards)
    setSelectedCard(response.data.cards[0] ?? null)
    setLoading(false)
  }

  async function onSelectCard(slug: string) {
    const response = await getTarotCard(slug)
    if (response.error || !response.data) {
      setErrorMessage(response.error?.message ?? 'Unable to load card')
      return
    }
    setSelectedCard(response.data.card)
  }

  const filteredCards = useMemo(() => cards, [cards])

  return (
    <main className="mx-auto min-h-screen w-full max-w-6xl p-6">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">Tarot Gallery</h1>
          <p className="text-sm text-zinc-400">Browse Rider-Waite-Smith cards with quick filters.</p>
        </div>
      </header>

      <section className="mb-4 rounded-lg border border-zinc-700 bg-zinc-900/70 p-4">
        <form className="grid gap-3 md:grid-cols-4" onSubmit={applyFilters}>
          <div>
            <label className="mb-1 block text-sm text-zinc-200" htmlFor="arcana">
              Arcana
            </label>
            <select
              id="arcana"
              value={arcana}
              onChange={(event) => setArcana(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
            >
              <option value="">Any</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-200" htmlFor="suit">
              Suit
            </label>
            <select
              id="suit"
              value={suit}
              onChange={(event) => setSuit(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
            >
              <option value="">Any</option>
              <option value="wands">Wands</option>
              <option value="cups">Cups</option>
              <option value="swords">Swords</option>
              <option value="pentacles">Pentacles</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-200" htmlFor="search">
              Search
            </label>
            <input
              id="search"
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              placeholder="Name or keyword"
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              className="w-full rounded-md bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950"
              disabled={loading}
            >
              {loading ? 'Loading…' : 'Apply filters'}
            </button>
          </div>
        </form>
        {errorMessage && <p className="mt-2 text-sm text-rose-400" role="alert">{errorMessage}</p>}
      </section>

      {loading ? (
        <p className="text-sm text-zinc-300">Loading cards…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <div className="md:col-span-2">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {filteredCards.map((card) => (
                <button
                  key={card.id}
                  type="button"
                  onClick={() => onSelectCard(card.slug)}
                  className="flex flex-col rounded-md border border-zinc-700 bg-zinc-900/60 p-3 text-left hover:border-zinc-500"
                >
                  <div className="relative h-40 w-full">
                    <Image
                      src={card.image}
                      alt={card.name}
                      fill
                      sizes="200px"
                      className="rounded-sm object-contain"
                    />
                  </div>
                  <div className="mt-2 text-sm text-zinc-100">{card.name}</div>
                  <div className="text-xs text-zinc-400">{card.arcana === 'major' ? 'Major Arcana' : `${card.suit ?? ''} • Minor`}</div>
                </button>
              ))}
            </div>
          </div>

          <aside className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-4">
            {selectedCard ? (
              <div>
                <h2 className="text-lg font-semibold text-zinc-100">{selectedCard.name}</h2>
                <p className="text-sm text-zinc-400">{selectedCard.description}</p>
                <div className="mt-3 text-sm text-zinc-200">
                  <div className="font-medium">Keywords</div>
                  <p className="text-zinc-300">{selectedCard.keywords.join(', ')}</p>
                </div>
                <div className="mt-3 text-sm text-emerald-300">
                  <div className="font-medium text-emerald-200">Upright</div>
                  <p>{selectedCard.upright.join(', ')}</p>
                </div>
                <div className="mt-3 text-sm text-amber-300">
                  <div className="font-medium text-amber-200">Reversed</div>
                  <p>{selectedCard.reversed.join(', ')}</p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-zinc-400">Select a card to view details.</p>
            )}
          </aside>
        </div>
      )}
    </main>
  )
}
