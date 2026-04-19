# UR Legacy Alias Retirement Checklist

Context:
- Legacy aliases: `año`, `mes`, `valor`.
- Canonical keys: `year`, `month`, `value`.
- Current behavior: canonical-only (`year/month/value`) after v1.5.0 cleanup.

## Target `v1.4.0` (hardening without breakage)

1. CI hardening
- [x] Enable `SIFU_LEGACY_ALIAS_WARNINGS=1` in backend test workflow.
- [x] Confirm no new failing tests due to deprecation warnings.

2. Test and code hygiene
- [x] Keep integration tests on canonical keys (`year/month/value`).
- [x] Keep at most one explicit compatibility assertion per area.
- [x] Ensure new tests do not introduce `año/mes/valor` unless marked as compatibility test.

3. Verification
- [x] Run focused suite: `tests/integration/test_ur.py`, `tests/test_ur_services.py`.
- [ ] Run backend main suite in CI with warnings enabled.

Estado actual:
- Validación local equivalente ejecutada: `pytest tests -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto` con `SIFU_LEGACY_ALIAS_WARNINGS=1` → 278 passed, 10 skipped.

## Target `v1.5.0` (final removal)

1. Code removal
- [x] Remove alias properties (`año/mes/valor`) from `URValue`.
- [x] Remove alias properties and alias-kwargs mapping from `URRecord`.
- [x] Remove `SIFU_LEGACY_ALIAS_WARNINGS` checks related only to UR aliases.

2. Test cleanup
- [x] Remove compatibility assertions relying on `año/mes/valor`.
- [x] Remove or repurpose `tests/test_legacy_alias_warnings.py`.

3. Contract and docs
- [x] Update docs to state only canonical keys are supported.
- [x] Add changelog entry for alias removal and migration note.

4. Final validation
- [x] Full backend test suite green.
- [x] API smoke checks for UR endpoints green.

Estado actual v1.5.0:
- Validación local: `pytest tests -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto` → 274 passed, 10 skipped.
- Changelog registrado: `CHANGELOG_2026-04-19.md` (sección "UR Alias Retirement (v1.5.0)").
- Pendiente para cierre formal: corrida CI completa en PR.
