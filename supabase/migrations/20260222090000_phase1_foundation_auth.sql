create extension if not exists pgcrypto;

create table if not exists public.app_users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  password_hash text not null,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.profiles (
  user_id uuid primary key references public.app_users(id) on delete cascade,
  display_name text not null,
  timezone text not null default 'UTC',
  locale text not null default 'en-US',
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.telemetry_events (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.app_users(id) on delete cascade,
  session_id uuid not null,
  event_name text not null,
  properties jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now())
);

create index if not exists telemetry_events_user_id_idx on public.telemetry_events (user_id);
create index if not exists telemetry_events_session_id_idx on public.telemetry_events (session_id);
create index if not exists telemetry_events_event_name_idx on public.telemetry_events (event_name);
create index if not exists telemetry_events_created_at_idx on public.telemetry_events (created_at desc);

create or replace function public.set_updated_at_timestamp()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
before update on public.profiles
for each row
execute function public.set_updated_at_timestamp();
