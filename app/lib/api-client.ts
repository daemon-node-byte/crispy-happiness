'use client'

import {
  ApiResponse,
  AuthCredentials,
  AuthSuccessData,
  SessionData,
  TelemetryEventInput,
  UserProfile,
  TarotListResponse,
  TarotCard,
  TarotReading,
  CardOfDay,
} from '@/app/lib/types'

const API_BASE = '/api'
const SESSION_TOKEN_KEY = 'astarot.session.token'

async function requestJson<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers ?? {}),
      },
      cache: 'no-store',
    })

    const payload = (await response.json()) as ApiResponse<T>
    if (!response.ok) {
      return {
        error: payload.error ?? {
          code: 'INTERNAL_ERROR',
          message: 'Request failed',
        },
      }
    }

    return payload
  } catch {
    return {
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Network error. Please try again.',
      },
    }
  }
}

function authHeaders(): HeadersInit {
  const token = getSessionToken()
  if (!token) {
    return {}
  }
  return { Authorization: `Bearer ${token}` }
}

export function getSessionToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }
  return window.localStorage.getItem(SESSION_TOKEN_KEY)
}

export function clearSessionToken(): void {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.removeItem(SESSION_TOKEN_KEY)
}

function persistToken(token: string): void {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.setItem(SESSION_TOKEN_KEY, token)
}

export async function signUp(
  credentials: AuthCredentials
): Promise<ApiResponse<AuthSuccessData>> {
  const response = await requestJson<AuthSuccessData>('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
  if (response.data?.token) {
    persistToken(response.data.token)
  }
  return response
}

export async function logIn(
  credentials: AuthCredentials
): Promise<ApiResponse<AuthSuccessData>> {
  const response = await requestJson<AuthSuccessData>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
  if (response.data?.token) {
    persistToken(response.data.token)
  }
  return response
}

export async function logOut(): Promise<ApiResponse<{ ok: boolean }>> {
  const response = await requestJson<{ ok: boolean }>('/auth/logout', {
    method: 'POST',
    headers: authHeaders(),
  })
  clearSessionToken()
  return response
}

export async function getSession(): Promise<ApiResponse<{ session: SessionData }>> {
  return requestJson<{ session: SessionData }>('/auth/session', {
    method: 'GET',
    headers: authHeaders(),
  })
}

export async function getProfile(): Promise<ApiResponse<{ profile: UserProfile }>> {
  return requestJson<{ profile: UserProfile }>('/profile', {
    method: 'GET',
    headers: authHeaders(),
  })
}

export async function updateProfile(input: {
  displayName?: string
  timezone?: string
  locale?: string
}): Promise<ApiResponse<{ profile: UserProfile }>> {
  return requestJson<{ profile: UserProfile }>('/profile', {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify(input),
  })
}

export async function logTelemetry(
  event: TelemetryEventInput
): Promise<ApiResponse<{ ok: boolean }>> {
  return requestJson<{ ok: boolean }>('/telemetry/events', {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(event),
  })
}

export async function listTarotCards(params?: {
  arcana?: string
  suit?: string
  search?: string
}): Promise<ApiResponse<TarotListResponse>> {
  const query = new URLSearchParams()
  if (params?.arcana) query.set('arcana', params.arcana)
  if (params?.suit) query.set('suit', params.suit)
  if (params?.search) query.set('search', params.search)

  const path = query.toString() ? `/tarot/cards?${query.toString()}` : '/tarot/cards'
  return requestJson<TarotListResponse>(path, { method: 'GET' })
}

export async function getTarotCard(slug: string): Promise<ApiResponse<{ card: TarotCard }>> {
  return requestJson<{ card: TarotCard }>(`/tarot/cards/${slug}`, { method: 'GET' })
}

export async function createReading(input: {
  spreadType?: string
  cardsCount?: number
}): Promise<ApiResponse<{ reading: TarotReading }>> {
  return requestJson<{ reading: TarotReading }>(`/readings`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(input),
  })
}

export async function listReadings(): Promise<ApiResponse<{ readings: TarotReading[] }>> {
  return requestJson<{ readings: TarotReading[] }>(`/readings`, {
    method: 'GET',
    headers: authHeaders(),
  })
}

export async function getCardOfDay(timezone?: string): Promise<ApiResponse<{ cardOfDay: CardOfDay }>> {
  const query = timezone ? `?timezone=${encodeURIComponent(timezone)}` : ''
  return requestJson<{ cardOfDay: CardOfDay }>(`/readings/card-of-day${query}`, {
    method: 'GET',
    headers: authHeaders(),
  })
}
