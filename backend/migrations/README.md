# Database migrations

Alembic migrations for the EyeDx backend. The database URL is read from
application settings (`DATABASE_URL`) at runtime; it is never stored in
`alembic.ini`.

## Requirements

- PostgreSQL 13 or newer. The schema uses `gen_random_uuid()` as a column
  default, which is built in from PostgreSQL 13. On older servers, enable the
  `pgcrypto` extension instead.

Apply migrations:

```bash
# from the backend/ directory
alembic upgrade head
```

## Revision chain (dependency ordered)

Revisions are ordered by foreign-key dependency, which is **not** the same as
the numeric prefix on each file. Always rely on `down_revision`, not on file
numbers.

| Revision                   | down_revision              | Tables created            |
| -------------------------- | -------------------------- | ------------------------- |
| 001_create_users           | (base)                     | roles, users              |
| 002_create_patients        | 001_create_users           | patients                  |
| 003_create_eye_images      | 002_create_patients        | eye_images                |
| 006_create_model_versions  | 003_create_eye_images      | model_versions            |
| 007_create_consents        | 006_create_model_versions  | consents                  |
| 004_create_predictions     | 007_create_consents        | predictions               |
| 005_create_reports         | 004_create_predictions     | reports                   |
| 008_create_audit_logs      | 005_create_reports         | audit_logs                |
| 009_create_prediction_items| 008_create_audit_logs      | prediction_items          |
| 010_create_refresh_tokens  | 009_create_prediction_items| refresh_tokens            |
| 011_create_system_events   | 010_create_refresh_tokens  | system_events             |

Enumerated columns use `native_enum=False` (stored as `VARCHAR`), so no
PostgreSQL enum types are created and no extension is required for them.

## Notes

- `metadata` columns are PostgreSQL `JSONB`.
- Reference data (RBAC roles) is seeded separately via
  `python -m app.database.seed`; migrations never insert clinical or user
  data.
