# Deployment Specification

## Backend — Railway
- Python 3.12, FastAPI
- DATABASE_URL from Railway PostgreSQL addon
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Run migrations on deploy: `alembic upgrade head && python -m app.seed`

## Frontend — Vercel
- Vite build, static output
- VITE_API_URL environment variable pointing to Railway backend

## Environment Variables
### Backend (.env)
- DATABASE_URL: PostgreSQL connection string
- CORS_ORIGINS: comma-separated allowed origins
- ENV: development | production

### Frontend (.env)
- VITE_API_URL: backend API base URL

## CORS Configuration
- Development: http://localhost:5173
- Production: Vercel deployment URL only (never `*`)

## QA requirements
- Verify `./scripts/check.sh` passes before every deployment (lint + security + tests)
- Backend: `python -m pytest tests/ -v` must pass
- Frontend: `npx vitest run` must pass
- All checks in `scripts/check.sh`: ruff, bandit, pip-audit, pytest, eslint, tsc, npm audit, vitest

## Security requirements

### Hardcoded values — zero tolerance
- No passwords, tokens, API keys, or connection strings anywhere in code
- All sensitive config comes from environment variables via pydantic-settings (backend) or Vite env (frontend)
- `.env` files must be gitignored — only `.env.example` with safe placeholder values is committed
- `.env.example` must contain only `localhost`/dummy values, never real credentials

### Environment variable exposure
- Backend: `DATABASE_URL`, `CORS_ORIGINS`, `ENV` — all via pydantic-settings `BaseSettings`, never hardcoded
- Frontend: only `VITE_API_URL` — no `VITE_SECRET_*`, `VITE_PASSWORD_*`, or `VITE_TOKEN_*`
- No env vars printed, logged, or exposed in error responses at any log level
- Production error responses must return generic messages, never stack traces or config values

### Dependency scanning
- `pip-audit` for backend Python packages — flag high/critical CVEs
- `npm audit --audit-level=moderate` for frontend — flag moderate+ vulnerabilities
- `bandit -r app/ -q` for Python security patterns (hardcoded passwords, exec usage, etc.)

### Pre-deployment checklist
1. `ENV=production` disables FastAPI docs (`/api/docs`)
2. `CORS_ORIGINS` set to exact Vercel domain (not `*`)
3. `DATABASE_URL` points to production PostgreSQL (not localhost)
4. No `.env` files deployed — all env vars set in Railway/Vercel dashboard
5. `./scripts/check.sh` exits 0
