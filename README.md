# KrishiMitra AI

**Predict. Advise. Act.** — Lenovo LEAP Hackathon, Theme 5: Smart Agriculture & Rural Innovation.

## Full MVP implementation status

All planned implementation phases are now represented in this repository:

- **Phase 0 — Scope:** requirements, architecture, acceptance criteria and seeded demo scenario reflected in code/docs.
- **Phase 1 — Foundation:** React/Vite/TypeScript/Tailwind/PWA shell, FastAPI service, health/readiness, Supabase extension migration, Docker.
- **Phase 2 — Auth & farm data:** Supabase JWT validation, profile/farm/crop/soil APIs, SQLAlchemy repositories, validation, idempotency, RLS migration, deterministic demo seed.
- **Phase 3 — App shell:** responsive mobile-first navigation, English/Hindi toggle, farm context, Home/Farm/Insights/Advisor/More surfaces, accessible targets and reduced-motion support.
- **Phase 4 — Weather & market:** adapter-ready insight endpoints with cached/freshness-shaped contracts and deterministic Kanpur demo fixtures; market history + forecast range + confidence + disclaimer.
- **Phase 5 — Risk & decision:** explainable risk factors and deterministic prioritized recommendation, including demo decision **“Avoid irrigation today”** from rain probability + soil moisture.
- **Phase 6 — Advisor/RAG contract:** advisor endpoint with language handling, approved-source IDs, farm-context framing and safety guardrails. The current fixture adapter is deterministic so the demo works without an LLM key.
- **Phase 7 — Quality/deploy groundwork:** migrations, API structure, PWA configuration, validation tests, compile checks, environment examples and Docker packaging.

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

If Supabase environment variables are absent, the UI runs in **seeded demo mode** so the hackathon flow can be demonstrated without credentials.

## Run backend

```bash
cd backend
python -m venv .venv
# activate the venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISSUER`, and other provider keys in `backend/.env` for connected mode.

## Supabase

Apply migrations in order:

1. `supabase/migrations/0001_extensions.sql`
2. `supabase/migrations/0002_core_schema.sql`
3. `supabase/migrations/0003_insights_and_knowledge.sql`

Migration 0003 adds a `SECURITY DEFINER` `is_admin()` helper to avoid recursive RLS checks from the initial policy design.

## Demo seed

```bash
python scripts/seed_demo.py
```

Defaults are documented in the script and can be overridden with environment variables.

## Verification completed in this environment

- Backend Python compilation: **passed**
- Backend tests: **3 passed**
- Frontend dependency installation/build could not be completed in the build environment because package installation timed out. The source and configuration are included for local `npm install && npm run build` verification.

## Important production follow-up

This is a complete hackathon MVP implementation scaffold with deterministic demo providers. Before production use, connect and test the real weather/market/LLM providers, apply migrations to a real Supabase project, run real cross-user RLS/E2E tests, add observability, and rehearse deployment.
