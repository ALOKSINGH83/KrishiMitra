-- Phase 4-6 persisted insight/advisor data. External provider responses are cached snapshots.
create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
stable
as $$ select exists (select 1 from public.profiles where id = auth.uid() and role = 'admin' and active = true); $$;
revoke all on function public.is_admin() from public;
grant execute on function public.is_admin() to authenticated;

-- Replace recursive admin checks from 0002 with the security-definer helper.
drop policy if exists profiles_select_self on public.profiles;
create policy profiles_select_self on public.profiles for select using (id = auth.uid() or public.is_admin());
drop policy if exists farms_owner_select on public.farms;
create policy farms_owner_select on public.farms for select using (user_id = auth.uid() or public.is_admin());
drop policy if exists farms_owner_update on public.farms;
create policy farms_owner_update on public.farms for update using (user_id = auth.uid() or public.is_admin()) with check (user_id = auth.uid() or public.is_admin());
drop policy if exists crops_owner_select on public.crops;
create policy crops_owner_select on public.crops for select using (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
drop policy if exists crops_owner_insert on public.crops;
create policy crops_owner_insert on public.crops for insert with check (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
drop policy if exists crops_owner_update on public.crops;
create policy crops_owner_update on public.crops for update using (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin()))) with check (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
drop policy if exists soil_owner_select on public.soil_readings;
create policy soil_owner_select on public.soil_readings for select using (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
drop policy if exists soil_owner_insert on public.soil_readings;
create policy soil_owner_insert on public.soil_readings for insert with check (exists (select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));

create table if not exists public.knowledge_chunks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text not null,
  source_name text not null,
  source_url text,
  approved boolean not null default false,
  embedding vector(1536),
  created_at timestamptz not null default now()
);
create index if not exists knowledge_chunks_approved_idx on public.knowledge_chunks(approved);

create table if not exists public.weather_snapshots (
  id uuid primary key default gen_random_uuid(), farm_id uuid not null references public.farms(id) on delete restrict,
  observed_at timestamptz not null, source text not null, payload jsonb not null, created_at timestamptz not null default now()
);
create index if not exists weather_snapshots_farm_time_idx on public.weather_snapshots(farm_id, observed_at desc);

create table if not exists public.risk_assessments (
  id uuid primary key default gen_random_uuid(), farm_id uuid not null references public.farms(id) on delete restrict,
  crop_id uuid references public.crops(id) on delete restrict, overall_score double precision not null check(overall_score between 0 and 1),
  payload jsonb not null, model_version text not null, created_at timestamptz not null default now()
);
create index if not exists risk_assessments_farm_time_idx on public.risk_assessments(farm_id, created_at desc);

create table if not exists public.recommendations (
  id uuid primary key default gen_random_uuid(), farm_id uuid not null references public.farms(id) on delete restrict,
  crop_id uuid references public.crops(id) on delete restrict, title text not null, priority text not null,
  why text not null, evidence jsonb not null default '[]', valid_until timestamptz not null,
  state text not null default 'generated' check(state in ('generated','active','acknowledged','completed','dismissed','expired')),
  created_at timestamptz not null default now()
);
create index if not exists recommendations_farm_state_idx on public.recommendations(farm_id,state,valid_until);

create table if not exists public.market_snapshots (
  id uuid primary key default gen_random_uuid(), commodity text not null, market text not null, payload jsonb not null,
  observed_at timestamptz not null, created_at timestamptz not null default now()
);

create table if not exists public.advisor_messages (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.profiles(id) on delete restrict,
  farm_id uuid references public.farms(id) on delete restrict, role text not null check(role in ('user','assistant')),
  content text not null, language text not null default 'en', source_ids jsonb not null default '[]', created_at timestamptz not null default now()
);

alter table public.knowledge_chunks enable row level security;
alter table public.weather_snapshots enable row level security;
alter table public.risk_assessments enable row level security;
alter table public.recommendations enable row level security;
alter table public.market_snapshots enable row level security;
alter table public.advisor_messages enable row level security;

create policy knowledge_admin_read on public.knowledge_chunks for select using (public.is_admin());
create policy weather_owner_read on public.weather_snapshots for select using (exists(select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
create policy risk_owner_read on public.risk_assessments for select using (exists(select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
create policy recommendations_owner_read on public.recommendations for select using (exists(select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
create policy recommendations_owner_update on public.recommendations for update using (exists(select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin()))) with check (exists(select 1 from public.farms f where f.id=farm_id and (f.user_id=auth.uid() or public.is_admin())));
create policy market_read_authenticated on public.market_snapshots for select using (auth.uid() is not null);
create policy advisor_owner_read on public.advisor_messages for select using (user_id=auth.uid() or public.is_admin());
create policy advisor_owner_insert on public.advisor_messages for insert with check (user_id=auth.uid());
