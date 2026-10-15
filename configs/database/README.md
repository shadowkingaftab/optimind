# Database Configuration

PostgreSQL configuration.
- DATABASE_URL: INPUT_REQUIRED (format: postgresql+asyncpg://user:pass@host:port/dbname)
- DB_POOL_SIZE: INPUT_REQUIRED (format: integer, default suggested 20)
- DB_MAX_OVERFLOW: INPUT_REQUIRED (format: integer)
- DB_POOL_TIMEOUT: 30 (default)

**Note**: Passwords in DATABASE_URL must come from secrets. Never log full URL.
**Consuming**: backend/database/engine.py, Alembic (Phase 2)
**Safe absence**: Fail fast on startup if DATABASE_URL missing or malformed (without logging credentials).
