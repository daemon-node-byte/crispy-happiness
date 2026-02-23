## Astarot — Tarot + Astrology Web App

Hybrid Next.js (frontend) + Flask (backend) monorepo with Supabase for auth/storage. Roadmap-driven build: Phase 1 (auth/foundation) and Phase 2 (tarot data/gallery) are complete.

### Stack
- Next.js App Router, React, TypeScript, Tailwind
- Flask Python API (Vercel serverless compatible)
- Supabase Postgres (via REST/service role) for persistence and auth trust
- YAML-backed tarot data with Rider-Waite-Smith assets

### Features (current)
- Auth flows (signup/login/logout), session tokens, profile update, telemetry logging
- Tarot card catalog with filters/search and detail view (Rider-Waite-Smith sample set)
- Protected dashboard shell

### Roadmap status
- Phase 1 — Foundation & Auth: ✅ complete
- Phase 2 — Tarot Card Data & Gallery: ✅ complete
- Next up: Phase 3 — Tarot Readings & Card of the Day (types → schema → API → clients → UI → tests)

### Quick start
1) Install JS deps: `pnpm install`
2) Install Python deps: `pip install -r requirements.txt`
3) Copy env template: `cp .env.example .env` and fill values (see Env section)
4) Run dev servers:
   - `pnpm dev` (runs Next + Flask concurrently via rewrites to http://127.0.0.1:5328)
5) Open http://localhost:3000

### Env
Create `.env` from `.env.example`:
- `SESSION_SECRET` — secret for signing session tokens
- `SESSION_TTL_SECONDS` — token lifetime
- `SUPABASE_URL` — your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — service role key for REST access
- `SUPABASE_SECRET_KEY` — Supabase JWT secret (if needed for local emulation)
- `NEXT_PUBLIC_API_BASE` — normally `/api`

### Supabase CLI
- Install (macOS): `brew install supabase/tap/supabase`
- Install (curl): `curl -fsSL https://supabase.com/cli/install.sh | sh`
- Login: `supabase login` (use a Supabase access token)
- Verify config: `supabase status`
- Migrations: `supabase db push` or `supabase db reset` (uses [supabase/migrations](supabase/migrations))

### API (Phase 1–2)
- `POST /api/auth/signup` — email/password signup
- `POST /api/auth/login` — login
- `POST /api/auth/logout` — logout
- `GET /api/auth/session` — current session
- `GET /api/profile`, `PATCH /api/profile` — profile read/update
- `POST /api/telemetry/events` — limited telemetry events
- `GET /api/tarot/cards` — list cards (filters: `arcana`, `suit`, `search`)
- `GET /api/tarot/cards/:slug` — card detail

### Frontend routes
- `/` — auth form
- `/dashboard` — protected dashboard shell
- `/tarot` — tarot gallery

### Data
- Tarot YAML seed: `data/tarot/cards.yaml`
- Rider-Waite-Smith images: `public/assets/images/decks/rider-waite`

### Testing
- Backend: `pytest`
- Frontend lint: `pnpm lint`

### Deployment notes
- Next rewrites proxy `/api/*` to Flask locally; in production the Flask handlers run as Vercel Python serverless functions. Keep paths stable (`/api/...`).
