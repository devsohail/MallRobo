# MallRobo — mall robot shopping-cart system (technical assessment)

Monorepo: backend/ (FastAPI, Python 3.12, uv) · frontend/ (React 18 + TS, Vite, Tailwind)

## Non-negotiables
- Read the relevant specs/*.md before implementing anything. Specs win over your instincts.
- Pathfinding logic lives in backend/app/pathfinding/ — pure Python, no FastAPI/SQLAlchemy imports.
- TypeScript strict; no `any`. Python fully type-hinted; ruff + mypy must pass.
- Every endpoint: Pydantic-validated input, structured error responses.
- Tests must pass before any commit: `cd backend && python -m pytest tests/ -v` · `cd frontend && npm test`.
- Every new feature must have tests. qa-engineer writes tests, runs them, then runs the full suite as sanity check. Bugs are logged in AI_REVIEW_LOG.md.
- Conventional commits: feat:/fix:/test:/docs:/chore:.

## Security non-negotiables
- Zero hardcoded secrets: no passwords, tokens, API keys, or connection strings in code. All sensitive values come from environment variables via `pydantic-settings`.
- `.env` files are gitignored. Only `.env.example` (with safe placeholder values) is committed.
- Frontend `VITE_*` vars are public — never put secrets there. Only `VITE_API_URL` is allowed.
- No env vars logged, printed, or exposed in error responses.
- All DB access via SQLAlchemy ORM/bound parameters — zero raw SQL string building.
- CORS restricted to specific origin in production (never `*`).
- `product_ids` capped at 50 to prevent algorithmic DoS against Held-Karp.
- FastAPI docs disabled in production (`ENV=production`).

## Commands
- backend dev: uvicorn app.main:app --reload
- db: alembic upgrade head · python -m app.seed
- frontend dev: npm run dev
- backend tests: cd backend && python -m pytest tests/ -v
- frontend tests: cd frontend && npx vitest run --reporter=verbose
- full check (lint + security + tests): ./scripts/check.sh

## Workflow
feature-dev implements → qa-engineer verifies → security-auditor audits → human reviews.

### Mandatory gates (every feature, no exceptions)
1. **feature-dev**: implement + write tests + all tests pass
2. **qa-engineer**: write additional tests, run full sanity suite, log any bugs in AI_REVIEW_LOG.md
3. **security-auditor**: scan for hardcoded values, env var exposure, API attack surface, dependency vulns — report findings (never fix)
4. **human**: reviews everything, logs corrections in AI_REVIEW_LOG.md

A feature is NOT done until all four gates pass. No gate may be skipped.
