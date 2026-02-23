'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import {
  createJournalEntry,
  deleteJournalEntry,
  exportJournalEntry,
  getSession,
  listJournalEntries,
  updateJournalEntry,
} from '@/app/lib/api-client'
import { JournalEntry, JournalExport, JournalExportFormat } from '@/app/lib/types'

function tagsFromInput(input: string): string[] {
  return input
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

export default function JournalPage() {
  const router = useRouter()
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [tagsInput, setTagsInput] = useState('')

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [pageError, setPageError] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const [exportResult, setExportResult] = useState<JournalExport | null>(null)

  useEffect(() => {
    void initialize()
  }, [])

  async function initialize() {
    setPageError(null)
    setLoading(true)

    const session = await getSession()
    if (session.error || !session.data) {
      setLoading(false)
      setPageError('Please sign in to access your journal.')
      router.replace('/')
      return
    }

    const response = await listJournalEntries()
    if (response.error) {
      setPageError(response.error.message)
      setLoading(false)
      return
    }

    const loadedEntries = response.data?.entries ?? []
    setEntries(loadedEntries)
    if (loadedEntries.length > 0) {
      selectEntry(loadedEntries[0])
    } else {
      resetForm()
    }
    setLoading(false)
  }

  function resetForm() {
    setSelectedId(null)
    setTitle('')
    setBody('')
    setTagsInput('')
    setExportResult(null)
    setFormError(null)
  }

  function selectEntry(entry: JournalEntry) {
    setSelectedId(entry.id)
    setTitle(entry.title)
    setBody(entry.body)
    setTagsInput(entry.tags.join(', '))
    setExportResult(null)
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setFormError(null)

    const tags = tagsFromInput(tagsInput)
    if (selectedId) {
      const response = await updateJournalEntry(selectedId, { title, body, tags })
      if (response.error || !response.data?.entry) {
        setFormError(response.error?.message ?? 'Unable to update entry')
        setSaving(false)
        return
      }
      const updated = response.data.entry
      setEntries((current) => current.map((entry) => (entry.id === updated.id ? updated : entry)))
      selectEntry(updated)
    } else {
      const response = await createJournalEntry({ title, body, tags })
      if (response.error || !response.data?.entry) {
        setFormError(response.error?.message ?? 'Unable to create entry')
        setSaving(false)
        return
      }
      const created = response.data.entry
      setEntries((current) => [created, ...current])
      selectEntry(created)
    }

    setSaving(false)
  }

  async function onDelete() {
    if (!selectedId) return
    setDeleting(true)
    setFormError(null)

    const response = await deleteJournalEntry(selectedId)
    if (response.error) {
      setFormError(response.error.message ?? 'Unable to delete entry')
      setDeleting(false)
      return
    }

    setEntries((current) => current.filter((entry) => entry.id !== selectedId))
    resetForm()
    setDeleting(false)
  }

  async function onExport(format: JournalExportFormat) {
    if (!selectedId) return
    setExporting(true)
    setFormError(null)

    const response = await exportJournalEntry(selectedId, format)
    if (response.error || !response.data) {
      setFormError(response.error?.message ?? 'Unable to export entry')
      setExporting(false)
      return
    }

    setExportResult(response.data)
    setExporting(false)
  }

  const selectedEntry = useMemo(() => entries.find((entry) => entry.id === selectedId), [entries, selectedId])

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl p-6">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100">Journal</h1>
          <p className="text-sm text-zinc-400">Capture reflections, tag them, and export when needed.</p>
        </div>
        <button
          type="button"
          onClick={resetForm}
          className="rounded-md border border-zinc-700 px-3 py-2 text-sm text-zinc-100"
        >
          New entry
        </button>
      </header>

      {loading ? (
        <p className="text-sm text-zinc-300">Loading journal…</p>
      ) : pageError ? (
        <p className="text-sm text-rose-400" role="alert">{pageError}</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          <section className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-4">
            <h2 className="text-lg font-semibold text-zinc-100">Entries</h2>
            <p className="text-sm text-zinc-400">Select an entry to edit.</p>
            <div className="mt-3 space-y-2">
              {entries.length === 0 && <p className="text-sm text-zinc-400">No entries yet.</p>}
              {entries.map((entry) => (
                <button
                  key={entry.id}
                  type="button"
                  onClick={() => selectEntry(entry)}
                  className={`flex w-full items-start justify-between rounded-md border px-3 py-2 text-left transition ${
                    selectedId === entry.id
                      ? 'border-zinc-400 bg-zinc-800 text-zinc-50'
                      : 'border-zinc-700 bg-zinc-950/40 text-zinc-200 hover:border-zinc-500'
                  }`}
                >
                  <div>
                    <div className="text-sm font-medium">{entry.title || 'Untitled'}</div>
                    <div className="text-xs text-zinc-400">
                      {new Date(entry.updatedAt).toLocaleString()}
                    </div>
                    {entry.tags.length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1 text-[11px] text-emerald-200">
                        {entry.tags.map((tag) => (
                          <span key={tag} className="rounded bg-emerald-900/60 px-2 py-0.5">{tag}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-zinc-700 bg-zinc-900/70 p-4 lg:col-span-2">
            <h2 className="text-lg font-semibold text-zinc-100">{selectedEntry ? 'Edit entry' : 'New entry'}</h2>
            <form className="mt-4 space-y-4" onSubmit={onSubmit}>
              <div>
                <label htmlFor="title" className="mb-1 block text-sm text-zinc-200">
                  Title
                </label>
                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
                  placeholder="Untitled entry"
                />
              </div>

              <div>
                <label htmlFor="tags" className="mb-1 block text-sm text-zinc-200">
                  Tags (comma separated)
                </label>
                <input
                  id="tags"
                  type="text"
                  value={tagsInput}
                  onChange={(event) => setTagsInput(event.target.value)}
                  className="w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100"
                  placeholder="insight, gratitude"
                />
              </div>

              <div>
                <label htmlFor="body" className="mb-1 block text-sm text-zinc-200">
                  Body
                </label>
                <textarea
                  id="body"
                  value={body}
                  onChange={(event) => setBody(event.target.value)}
                  className="min-h-[200px] w-full rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
                  placeholder="Write your reflection here…"
                />
              </div>

              {formError && (
                <p role="alert" className="text-sm text-rose-400">
                  {formError}
                </p>
              )}

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-md bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-950 disabled:opacity-60"
                >
                  {saving ? 'Saving…' : selectedEntry ? 'Update entry' : 'Create entry'}
                </button>
                {selectedEntry && (
                  <button
                    type="button"
                    onClick={onDelete}
                    disabled={deleting}
                    className="rounded-md border border-rose-500 px-3 py-2 text-sm text-rose-200 disabled:opacity-60"
                  >
                    {deleting ? 'Deleting…' : 'Delete entry'}
                  </button>
                )}
                {selectedEntry && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => onExport('markdown')}
                      disabled={exporting}
                      className="rounded-md border border-zinc-600 px-3 py-2 text-sm text-zinc-100 disabled:opacity-60"
                    >
                      {exporting ? 'Exporting…' : 'Export markdown'}
                    </button>
                    <button
                      type="button"
                      onClick={() => onExport('html')}
                      disabled={exporting}
                      className="rounded-md border border-zinc-600 px-3 py-2 text-sm text-zinc-100 disabled:opacity-60"
                    >
                      {exporting ? 'Exporting…' : 'Export HTML'}
                    </button>
                  </div>
                )}
              </div>
            </form>

            {exportResult && (
              <div className="mt-6 rounded-md border border-zinc-700 bg-zinc-950/60 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <div className="text-sm text-zinc-300">
                    Exported as {exportResult.format.toUpperCase()}
                  </div>
                </div>
                <pre className="whitespace-pre-wrap text-sm text-zinc-100">{exportResult.content}</pre>
              </div>
            )}
          </section>
        </div>
      )}
    </main>
  )
}
