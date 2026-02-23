'use client'

import Image from 'next/image'
import { useEffect, useState } from 'react'

import { createReading, getCardOfDay, getSession, listReadings } from '@/app/lib/api-client'
import { CardOfDay, TarotReading } from '@/app/lib/types'

export default function ReadingsPage() {
  const [cardOfDay, setCardOfDay] = useState<CardOfDay | null>(null)
  const [readings, setReadings] = useState<TarotReading[]>([])
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [drawing, setDrawing] = useState(false)

  useEffect(() => {
    void init()
  }, [])

  async function init() {
    setLoading(true)
    const session = await getSession()
    if (session.error) {
      setErrorMessage('Please sign in to view readings.')
      setLoading(false)
      return
    }
    const timezone = session.data?.session.profile.timezone ?? 'UTC'

    const [cod, history] = await Promise.all([
      getCardOfDay(timezone),
      listReadings(),
    ])

    if (cod.data?.cardOfDay) setCardOfDay(cod.data.cardOfDay)
    if (history.data?.readings) setReadings(history.data.readings)
    setLoading(false)
  }

  async function onDraw() {
    setDrawing(true)
    const response = await createReading({ spreadType: 'three-card', cardsCount: 3 })
    if (response.error || !response.data) {
      setErrorMessage(response.error?.message ?? 'Unable to create reading')
      setDrawing(false)
      return
    }
    const reading = response.data.reading
    if (reading) {
      setReadings((current) => [reading, ...current])
    }
    setDrawing(false)
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl p-6">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">Readings</h1>
          <p className="text-sm text-zinc-400">Draw a three-card reading and view today’s card.</p>
        </div>
        <button
          type="button"
          onClick={onDraw}
          disabled={drawing}
          className="rounded-md bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950 disabled:opacity-60"
        >
          {drawing ? 'Drawing…' : 'Draw a reading'}
        </button>
      </header>

      {loading ? (
        <p className="text-sm text-zinc-300">Loading…</p>
      ) : errorMessage ? (
        <p className="text-sm text-rose-400" role="alert">{errorMessage}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <section className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-4 md:col-span-2">
            <h2 className="text-lg font-semibold text-zinc-100">History</h2>
            <p className="text-sm text-zinc-400">Latest readings first.</p>
            <div className="mt-3 space-y-3">
              {readings.length === 0 && <p className="text-sm text-zinc-400">No readings yet.</p>}
              {readings.map((reading) => (
                <div key={reading.id} className="rounded-md border border-zinc-700 bg-zinc-950/60 p-3">
                  <div className="flex items-center justify-between text-sm text-zinc-300">
                    <span>{reading.spreadType}</span>
                    <span>{new Date(reading.createdAt).toLocaleString()}</span>
                  </div>
                  <div className="mt-2 flex gap-2">
                    {reading.cards.map((card) => (
                      <span key={card.slug} className="rounded bg-zinc-800 px-2 py-1 text-xs text-zinc-200">
                        {card.slug} ({card.orientation})
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <aside className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-4">
            <h2 className="text-lg font-semibold text-zinc-100">Card of the Day</h2>
            {cardOfDay ? (
              <div className="mt-3 space-y-2">
                <div className="relative h-48 w-full">
                  <Image
                    src={cardOfDay.image}
                    alt={cardOfDay.name}
                    fill
                    sizes="220px"
                    className="rounded-md object-contain"
                  />
                </div>
                <div className="text-sm text-zinc-100">{cardOfDay.name}</div>
                <div className="text-xs text-zinc-400">For {cardOfDay.forDate} ({cardOfDay.timezone})</div>
                <div className="text-xs text-emerald-200">Upright: {cardOfDay.upright.join(', ')}</div>
                <div className="text-xs text-amber-200">Reversed: {cardOfDay.reversed.join(', ')}</div>
              </div>
            ) : (
              <p className="text-sm text-zinc-400">Unavailable.</p>
            )}
          </aside>
        </div>
      )}
    </main>
  )
}
