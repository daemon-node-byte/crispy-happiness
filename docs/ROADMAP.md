🧭 Tarot & Astrology Web App — MVP Development Roadmap

Purpose:
This document defines the MVP scope, development phases, and tracking structure for building a monorepo tarot + astrology web application.
It is designed for an AI coding agent to plan, execute, and track progress while respecting architectural constraints and future extensibility.

0. Constraints & Non-Negotiables

Monorepo structure is fixed

Flask (Python) backend via Vercel API proxy

Next.js + React + TypeScript frontend

No deployment changes

Extend cleanly; do not restructure existing apps

MVP must be:

Secure

Accessible

Localization-ready

Maintainable

1. MVP Definition (Scope Control)
✅ INCLUDED IN MVP (v1)
Core Tarot

Rider–Waite–Smith deck

Tarot card data (YAML-backed)

Card gallery

Tarot reading flow

Card of the Day

Tarot journal

Default spreads

Custom spread creator (basic but usable)

Core Astrology

User astrological profile

Natal chart calculation (pyswisseph)

Natal chart SVG rendering

Basic synastry chart

Simple daily/transit overview

Astrological information center

Platform

Supabase Auth (email + Google/Apple)

Supabase Postgres DB

Telemetry (non-sensitive events only)

User dashboard

Data export & account deletion

🚫 EXCLUDED FROM MVP (Planned for v2)

Admin/editor UI

Client-side encryption

Public journal sharing

Celery + Redis async workers

Advanced transit analysis

Persistent dice history

Full moderation UI

Rule: MVP ships usable value before deep expansion.

2. High-Level Architecture Plan
Backend (Flask)

REST-only JSON API

Feature-based module structure

Stateless endpoints

Cached astrology computations

YAML → service layer → API

Frontend (Next.js)

App Router (where applicable)

Server Components for content pages

Client Components for:

Tarot readings

Spread editor

Charts

Zustand for session state

Typed API clients

3. Development Phases & Milestones

Each phase must be completed and tested before moving on.

Phase 1 — Foundation & Auth

Status: ✅ Completed (2026-02-22)

Goal: Establish secure baseline and shared infrastructure.

Backend

Supabase connection

Auth helpers

User profile model

Telemetry events table

Central config module

Frontend

Auth flows (login/signup/reset)

Session handling

Protected routes

Dashboard shell

Dark theme base styling

Exit Criteria

User can sign up, log in, log out

Dashboard loads with authenticated session

Telemetry events logged safely

Phase 2 — Tarot Card Data & Gallery

Status: ✅ Completed (2026-02-22)

Goal: Canonical tarot data + browsing experience.

Backend

Tarot card schema

YAML loader

Read-only card endpoints

Frontend

Card gallery

Filters (arcana, suit, element)

Card detail page

Artwork skin toggling (locked/unlocked UI)

Exit Criteria

Cards render correctly

Data is centralized and future-DB ready

Phase 3 — Tarot Readings & Card of the Day

Status: ✅ Completed (2026-02-23)

Goal: Core tarot experience.

Backend

Reading model

Shuffle & draw logic

Card of the Day logic (timezone-safe)

Frontend

Reading flow UI

GSAP shuffle & flip animations

Spread position layout

Card flipping interaction

Card of the Day widget

Exit Criteria

User completes a reading end-to-end

Readings persist

Card of the Day is stable per day

Phase 4 — Tarot Journal

Status: ✅ Completed (2026-02-23)

Goal: Reflection, persistence, and privacy.

Backend

Journal entry model

CRUD endpoints

Export endpoints

Frontend

Journal list

Entry editor

Filters/search

Export UI (Markdown/HTML)

Exit Criteria

Entries are private

User can edit/delete/export safely

Phase 5 — Spreads & Custom Spread Editor

Goal: User creativity and reuse.

Backend

Spread model

Versioning

Public/private flags

Reporting model

Frontend

Konva-based spread editor

Drag/drop, rotate, snap

Spread browser

Fork spread flow

Exit Criteria

User creates and reuses spreads

Public/private behavior works

Phase 6 — Astrology Core (Natal Charts)

Goal: Reliable astrology foundation.

Backend

Birth data handling

Geocoding integration

pyswisseph services

Natal chart storage

Frontend

Profile form

SVG chart renderer

Placement descriptions

Export (SVG/PNG)

Exit Criteria

Natal charts compute accurately

SVG renders correctly

Data is reusable

Phase 7 — Synastry, Transits & Dice

Goal: Expanded astrology tools.

Backend

Synastry calculations

Basic transit logic

Dice roll logic

Frontend

Synastry SVG renderer

Transit overview UI

Dice animation (Konva + GSAP)

Exit Criteria

Synastry charts render

Dice rolls animate smoothly

Phase 8 — Info Center, Polish & QA

Goal: Ship-quality MVP.

Tasks

Astrology info pages (SSG/SEO)

Accessibility audit

Localization prep

Performance pass

Test coverage >90%

Account deletion & data export validation

Exit Criteria

MVP ready for public release

4. Progress Tracking Rules (For the Agent)

Each phase must have:

Types defined first

DB schema updated

API implemented

Frontend integrated

Tests added

Do not skip phases

Do not mix v2 features into v1

Keep diffs small and reviewable

5. v2 Preparation Checklist (Structure Only)

Admin role tables (empty)

Encryption-ready data fields

Async task interface stubs

Feature flags

Analytics abstraction layer