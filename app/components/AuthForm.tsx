'use client'

import { FormEvent, useMemo, useState } from 'react'

import { logIn, signUp } from '@/app/lib/api-client'
import { AuthSuccessData } from '@/app/lib/types'

type Mode = 'login' | 'signup'

interface AuthFormProps {
  onAuthenticated: (data: AuthSuccessData) => void
}

export function AuthForm({ onAuthenticated }: AuthFormProps) {
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [timezone, setTimezone] = useState('UTC')
  const [locale, setLocale] = useState('en-US')
  const [busy, setBusy] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const submitLabel = useMemo(() => (mode === 'login' ? 'Sign in' : 'Create account'), [mode])

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setErrorMessage(null)

    const credentials = {
      email,
      password,
      displayName: displayName || undefined,
      timezone,
      locale,
    }

    const response =
      mode === 'login' ? await logIn(credentials) : await signUp(credentials)

    if (response.error || !response.data) {
      setErrorMessage(response.error?.message ?? 'Unable to authenticate')
      setBusy(false)
      return
    }

    onAuthenticated(response.data)
    setBusy(false)
  }

  return (
    <section className="w-full max-w-md rounded-lg border border-zinc-700 bg-zinc-900/80 p-6">
      <h1 className="text-xl font-semibold text-zinc-100">Tarot + Astrology Portal</h1>
      <p className="mt-2 text-sm text-zinc-400">Sign in to access your private dashboard.</p>

      <div className="mt-4 flex gap-2" role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'login'}
          onClick={() => setMode('login')}
          className="rounded-md border border-zinc-600 px-3 py-2 text-sm text-zinc-100"
        >
          Sign in
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'signup'}
          onClick={() => setMode('signup')}
          className="rounded-md border border-zinc-600 px-3 py-2 text-sm text-zinc-100"
        >
          Create account
        </button>
      </div>

      <form className="mt-4 space-y-4" onSubmit={onSubmit}>
        <div>
          <label htmlFor="email" className="mb-1 block text-sm text-zinc-200">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1 block text-sm text-zinc-200">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
          />
        </div>

        {mode === 'signup' && (
          <>
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
          </>
        )}

        {errorMessage && (
          <p role="alert" className="text-sm text-rose-400">
            {errorMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-md bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950 disabled:opacity-60"
        >
          {busy ? 'Please wait…' : submitLabel}
        </button>
      </form>
    </section>
  )
}
