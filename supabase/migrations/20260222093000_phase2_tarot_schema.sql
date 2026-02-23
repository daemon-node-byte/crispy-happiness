create extension if not exists pg_trgm;

create table if not exists public.tarot_decks (
  id text primary key,
  name text not null,
  slug text not null unique,
  description text default ''
);

create table if not exists public.tarot_cards (
  id text primary key,
  deck_id text not null references public.tarot_decks(id) on delete cascade,
  name text not null,
  slug text not null unique,
  arcana text not null check (arcana in ('major', 'minor')),
  suit text check (suit in ('wands', 'cups', 'swords', 'pentacles')),
  card_number integer,
  keywords text[] not null default '{}',
  description text not null,
  upright text[] not null default '{}',
  reversed text[] not null default '{}',
  image text not null,
  created_at timestamptz not null default timezone('utc', now())
);

create index if not exists tarot_cards_arcana_idx on public.tarot_cards (arcana);
create index if not exists tarot_cards_suit_idx on public.tarot_cards (suit);
create index if not exists tarot_cards_deck_idx on public.tarot_cards (deck_id);
create index if not exists tarot_cards_name_trgm_idx on public.tarot_cards using gin (name gin_trgm_ops);

create table if not exists public.tarot_readings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.app_users(id) on delete cascade,
  spread_type text not null,
  seed text not null,
  cards jsonb not null,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.card_of_day (
  user_id uuid not null references public.app_users(id) on delete cascade,
  for_date date not null,
  timezone text not null default 'UTC',
  card_slug text not null,
  created_at timestamptz not null default timezone('utc', now()),
  primary key (user_id, for_date)
);
