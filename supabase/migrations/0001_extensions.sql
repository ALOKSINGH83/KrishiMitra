-- KrishiMitra AI foundation migration.
-- Supabase Auth owns auth.users. Application tables and RLS are introduced in Phase 2.
create extension if not exists pgcrypto;
create extension if not exists vector;
