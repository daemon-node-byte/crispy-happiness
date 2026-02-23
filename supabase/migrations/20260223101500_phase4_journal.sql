create table if not exists public.journal_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.app_users(id) on delete cascade,
  title text not null default '',
  body text not null default '',
  tags text[] not null default '{}',
  is_deleted boolean not null default false,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists journal_entries_user_id_idx on public.journal_entries (user_id);
create index if not exists journal_entries_created_at_idx on public.journal_entries (created_at desc);

create or replace function public.set_journal_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists set_journal_updated_at on public.journal_entries;
create trigger set_journal_updated_at
before update on public.journal_entries
for each row
execute function public.set_journal_updated_at();
