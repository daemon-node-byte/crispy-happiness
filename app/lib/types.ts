export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'VALIDATION_ERROR'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR'

export interface ApiError {
  code: ApiErrorCode
  message: string
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
}

export interface AuthUser {
  id: string
  email: string
}

export interface UserProfile {
  userId: string
  displayName: string
  timezone: string
  locale: string
  createdAt: string
  updatedAt: string
}

export type TelemetryEventName =
  | 'auth_signup_success'
  | 'auth_login_success'
  | 'auth_logout'
  | 'dashboard_view'

export interface TelemetryEventInput {
  eventName: TelemetryEventName
  sessionId: string
  properties?: Record<string, string | number | boolean | null>
}

export interface SessionData {
  sessionId: string
  user: AuthUser
  profile: UserProfile
  expiresAt: string
}

export interface AuthSuccessData {
  token: string
  session: SessionData
}

export interface AuthCredentials {
  email: string
  password: string
  displayName?: string
  timezone?: string
  locale?: string
}

export type Arcana = 'major' | 'minor'
export type Suit = 'wands' | 'cups' | 'swords' | 'pentacles'

export interface TarotCard {
  id: string
  name: string
  slug: string
  arcana: Arcana
  suit?: Suit
  number?: number
  keywords: string[]
  description: string
  upright: string[]
  reversed: string[]
  image: string
}

export interface TarotListResponse {
  cards: TarotCard[]
}

export type CardOrientation = 'upright' | 'reversed'

export interface DrawnCard {
  slug: string
  orientation: CardOrientation
}

export interface TarotReading {
  id: string
  spreadType: string
  seed: string
  cards: DrawnCard[]
  createdAt: string
}

export interface CardOfDay {
  slug: string
  name: string
  image: string
  keywords: string[]
  upright: string[]
  reversed: string[]
  forDate: string
  timezone: string
}

export interface JournalEntry {
  id: string
  title: string
  body: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

export type JournalExportFormat = 'markdown' | 'html'

export interface JournalExport {
  entryId: string
  format: JournalExportFormat
  content: string
}
