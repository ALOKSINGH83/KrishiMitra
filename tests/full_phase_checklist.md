# Full phase checklist

- [x] Phase 0: scope and architecture
- [x] Phase 1: foundation
- [x] Phase 2: authentication, data, RLS, validation, idempotency, demo seed
- [x] Phase 3: mobile-first app shell and bilingual UX
- [x] Phase 4: weather and market contracts + deterministic demo adapters
- [x] Phase 5: explainable risk and recommendation decision
- [x] Phase 6: advisor contract, source IDs, language and safety fallback
- [x] Phase 7: PWA/Docker/migrations/tests/packaging groundwork

## Verification

- `python -m compileall -q backend` — pass
- `pytest -q` — pass (3 tests)
- `npm install` / `npm run build` — not completed in this environment because dependency installation timed out; run locally before deployment.
