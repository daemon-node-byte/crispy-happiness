'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import { getSession, logOut, logTelemetry, updateProfile } from '@/app/lib/api-client'
import { SessionData } from '@/app/lib/types'

export function DashboardShell() {
  const router = useRouter()
  const [session, setSession] = useState<SessionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [displayName, setDisplayName] = useState('')
  const [timezone, setTimezone] = useState('UTC')
  const [locale, setLocale] = useState('en-US')

  useEffect(() => {
    let mounted = true

    async function initializeSession() {
      const response = await getSession()
      if (!mounted) {
        return
      }

      if (response.error || !response.data) {
        router.replace('/')
        return
      }

      const currentSession = response.data.session
      setSession(currentSession)
      setDisplayName(currentSession.profile.displayName)
      setTimezone(currentSession.profile.timezone)
      setLocale(currentSession.profile.locale)
      setLoading(false)

      await logTelemetry({
        eventName: 'dashboard_view',
        sessionId: currentSession.sessionId,
        properties: { screen: 'dashboard' },
      })
    }

    void initializeSession()

    return () => {
      mounted = false
    }
  }, [router])

  const greeting = useMemo(() => {
    if (!session) {
      return 'Welcome'
    }
    return `Welcome, ${session.profile.displayName}`
  }, [session])

  async function onProfileSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setErrorMessage(null)

    const response = await updateProfile({ displayName, timezone, locale })
    if (response.error || !response.data) {
      setSaving(false)
      setErrorMessage(response.error?.message ?? 'Unable to save profile')
      return
    }

    const updatedProfile = response.data.profile

    setSession((current) => {
      if (!current) {
        return current
      }
      return {
        ...current,
        profile: updatedProfile,
      }
    })
    setSaving(false)
  }

  async function onSignOut() {
    await logOut()
    router.replace('/')
  }

  if (loading) {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center p-6">
        <p className="text-sm text-zinc-300">Loading dashboard…</p>
      </main>
    )
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-3xl p-6">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">{greeting}</h1>
          <p className="mt-1 text-sm text-zinc-400">Authenticated dashboard shell is active.</p>
        </div>
        <button
          type="button"
          onClick={onSignOut}
          className="rounded-md border border-zinc-600 px-3 py-2 text-sm text-zinc-100"
        >
          Sign out
        </button>
      </header>

      <section className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-6">
        <h2 className="text-lg font-medium text-zinc-100">Profile</h2>
        <p className="mt-1 text-sm text-zinc-400">Update your baseline account preferences.</p>

        <form className="mt-4 space-y-4" onSubmit={onProfileSave}>
          <div>
            <label htmlFor="displayName" className="mb-1 block text-sm text-zinc-200">
              Display name
            </label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
            />
          </div>

          <div>
            <label htmlFor="timezone" className="mb-1 block text-sm text-zinc-200">
              Timezone
            </label>
            <input
              id="timezone"
              type="text"
              value={timezone}
              onChange={(event) => setTimezone(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
            />
          </div>

          <div>
            <label htmlFor="locale" className="mb-1 block text-sm text-zinc-200">
              Locale
            </label>
            <input
              id="locale"
              type="text"
              value={locale}
              onChange={(event) => setLocale(event.target.value)}
              className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
            />
          </div>

          {errorMessage && (
            <p role="alert" className="text-sm text-rose-400">
              {errorMessage}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950 disabled:opacity-60"
          >
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </form>
      </section>
    </main>
  )
}
