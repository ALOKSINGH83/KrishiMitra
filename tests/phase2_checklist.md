# Phase 2 checklist

- [x] JWT bearer dependency derives user identity from token `sub`.
- [x] Profile GET/PATCH route.
- [x] Farm create/list/get/update/archive routes.
- [x] Crop create/list/update routes nested under farm ownership.
- [x] Soil reading create/list routes.
- [x] Farm/crop/soil validation contracts.
- [x] Soil POST requires `Idempotency-Key`.
- [x] Frontend farm setup screen.
- [ ] Replace in-memory repositories with SQLAlchemy/Supabase repositories.
- [ ] Add real Supabase Auth client/session handling.
- [ ] Add database RLS policies and negative cross-owner tests.
- [ ] Add deterministic demo seed.
