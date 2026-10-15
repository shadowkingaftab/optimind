# EyeDx Backend

FastAPI backend for the EyeDx ocular screening platform.

> **Screening aid only.** This software does not provide a medical diagnosis
> and must not be used as a substitute for review by a qualified healthcare
> professional.

## Status

Phase 2 — backend foundation. This phase provides configuration, security
primitives, the async database layer, ORM models, the exception/error
contract, HTTP middleware, base schemas, the application factory, and the
initial Alembic migration set. **API endpoints (auth, uploads, predictions,
reports, health) are implemented in Phase 3.**

## Layout

```
app/
  core/         settings, security, logging, request context, permissions
  database/     declarative base, engine, sessions, health probe, seed
  models/       SQLAlchemy ORM models
  exceptions/   domain exceptions mapped to the ErrorResponse contract
  middleware/   request id, logging, security headers, cors, rate limit, size
  schemas/      shared pydantic schemas (common, errors, pagination, health)
  api/          router wiring and shared dependencies
  main.py       application factory (app.main:app)
  lifespan.py   startup/shutdown
migrations/     Alembic environment and revisions
```

## Requirements

- Python 3.11+
- PostgreSQL 13+ (the schema uses `gen_random_uuid()`)

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.example .env            # then fill in DATABASE_URL and JWT_SECRET_KEY
```

## Run (development)

```bash
alembic upgrade head
python -m app.database.seed     # seeds RBAC roles
uvicorn app.main:app --reload
```

Interactive docs are served at `/docs` once the app is running.

## Migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

See `migrations/README.md` for the dependency-ordered revision chain.

## Configuration

All configuration is environment-driven; see `.env.example`. The backend
fails fast at startup when `DATABASE_URL` is missing, or when
`JWT_SECRET_KEY` is missing in production. Secrets are held as `SecretStr`
and are never logged.

## Testing

The test suite lives in `tests/` and is executed in Phase 13. Do not run it
during foundation phases.
