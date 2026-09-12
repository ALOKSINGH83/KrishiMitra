-- Core persisted data + ownership RLS. auth.users is managed by Supabase Auth.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete restrict,
  display_name text,
  phone text,
  preferred_language text not null default 'en' check (preferred_language in ('en','hi')),
  role text not null default 'farmer' check (role in ('farmer','admin')),
  active boolean not null default true
);

create table if not exists public.farms (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete restrict,
  name text not null check (char_length(name) between 2 and 80),
  village text,
  district text not null,
  state text not null,
  pincode text,
  latitude double precision check (latitude between -90 and 90),
  longitude double precision check (longitude between -180 and 180),
  area numeric(12,3) not null check (area > 0),
  unit text not null default 'acre' check (unit in ('acre','hectare')),
  soil_type text,
  archived_at timestamptz
);

create table if not exists public.crops (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete restrict,
  crop_code text not null,
  name text not null,
  variety text,
  sowing_date date not null,
  growth_stage text not null check (growth_stage in ('sowing','germination','vegetative','flowering','fruiting','maturity','harvested')),
  expected_harvest_date date,
  area numeric(12,3) not null check (area > 0),
  status text not null default 'active' check (status in ('active','archived')),
  check (expected_harvest_date is null or expected_harvest_date >= sowing_date)
);

create table if not exists public.soil_readings (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete restrict,
  source text not null check (source in ('manual','sensor')),
  moisture double precision check (moisture between 0 and 100),
  ph double precision check (ph between 0 and 14),
  nitrogen double precision check (nitrogen between 0 and 500),
  phosphorus double precision check (phosphorus between 0 and 500),
  potassium double precision check (potassium between 0 and 500),
  temperature_c double precision check (temperature_c between -10 and 70),
  recorded_at timestamptz not null,
  notes text,
  check (moisture is not null or ph is not null or nitrogen is not null or phosphorus is not null or potassium is not null or temperature_c is not null)
);

create index if not exists farms_user_id_idx on public.farms(user_id);
create index if not exists crops_farm_id_idx on public.crops(farm_id);
create index if not exists soil_readings_farm_recorded_idx on public.soil_readings(farm_id, recorded_at desc);

alter table public.profiles enable row level security;
alter table public.farms enable row level security;
alter table public.crops enable row level security;
alter table public.soil_readings enable row level security;

-- Profiles: self or admin.
drop policy if exists profiles_select_self on public.profiles;
create policy profiles_select_self on public.profiles for select using (id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'));
drop policy if exists profiles_update_self on public.profiles;
create policy profiles_update_self on public.profiles for update using (id = auth.uid()) with check (id = auth.uid());

-- Farms: owner or admin.
drop policy if exists farms_owner_select on public.farms;
create policy farms_owner_select on public.farms for select using (user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'));
drop policy if exists farms_owner_insert on public.farms;
create policy farms_owner_insert on public.farms for insert with check (user_id = auth.uid());
drop policy if exists farms_owner_update on public.farms;
create policy farms_owner_update on public.farms for update using (user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin')) with check (user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'));

-- Child rows are protected through their farm owner.
drop policy if exists crops_owner_select on public.crops;
create policy crops_owner_select on public.crops for select using (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'))));
drop policy if exists crops_owner_insert on public.crops;
create policy crops_owner_insert on public.crops for insert with check (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'))));
drop policy if exists crops_owner_update on public.crops;
create policy crops_owner_update on public.crops for update using (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin')))) with check (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'))));

drop policy if exists soil_owner_select on public.soil_readings;
create policy soil_owner_select on public.soil_readings for select using (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'))));
drop policy if exists soil_owner_insert on public.soil_readings;
create policy soil_owner_insert on public.soil_readings for insert with check (exists (select 1 from public.farms f where f.id = farm_id and (f.user_id = auth.uid() or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin'))));

create table if not exists public.idempotency_keys (
  user_id uuid not null references public.profiles(id) on delete restrict,
  key text not null,
  operation text not null,
  response_id uuid,
  created_at timestamptz not null default now(),
  primary key (user_id, key, operation)
);
create index if not exists idempotency_created_idx on public.idempotency_keys(created_at);
