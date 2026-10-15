# EyeDx Phase 3 - Backend workflows implementation

**Phase:** 3  
**Status:** COMPLETED (partial: API routes, notifications, monitoring, jobs implemented; packaging updated; Phase 3 disposition report produced)  
**Commit range:** includes files added in Phase 3  
**Date:** 2026-10-15

## Purpose
This report summarises the Phase 3 implementation. Phase 3 extends Phase 2 backend foundation with preprocessing/storage/inference/repositories/audit/auth/authz/services/schemas/dependencies/routes, and adds notifications/monitoring/jobs stubs. Tests/builds/linters/migrations/servers/debug were not executed per rules.

## Inputs (required / present)
- Contracts: `contracts/openapi/backend-api.yaml` (paths: /health, /predictions; tags Auth, Predictions, Health), `contracts/json-schemas/*` present.
- Configs: `configs/security/{password-policy,rate-limits,retention-policy,allowed-origins}.yaml` present; stubs exist for upload-policy, some inference/storage/testing (documented).
- Settings (ENV-driven): `DATABASE_URL`, `JWT_SECRET_KEY` (prod), `MODEL_SERVICE_URL` (unless mock non-prod), `CORS_ALLOW_ORIGINS`, plus S3_* if used. Added `inference_mock_result` (default "abstained").
- Dependencies: requirements updated (`pillow>=10.2,<12.0`); optional reportlab/boto3 may be added per deployment (documented).

## What was implemented (non-exhaustive)
- **Settings**: extended `app/core/settings.py` with `inference_mock_result: str = "abstained"`.
- **Dependencies**: `app/api/dependencies.py` extended (SessionDep, service deps, PageParamsDep, SessionServiceDep).
- **Preprocessing**: `file_validator`, `image_decoder`, `image_metadata`, `image_sanitizer` (trimmed PIL import), `image_quality_gateway`, `preprocessing_contract`.
- **Storage**: interface, `file_naming` (`build_key`/`quarantine_key`), `signed_urls` (JWT HMAC), `local_storage` (path traversal guard, `/api/v1/files/{token}`), `object_storage` (lazy boto3), `retention_policy`; `get_storage()`/`reset_storage()`.
- **Inference**: contract, circuit breaker, retry policy, request builder, response mapper, http client, mock client (allowed {abstained, uncertain, low_quality}, never success); `get_inference_client()`/`close_inference_client()`.
- **Repositories**: base + user/role/patient/consent/eye_image/prediction/model_version/report/refresh_token/audit/system_event. Added `count_for_patient` to prediction/report repositories.
- **Audit**: events, context, logger with `record_independent` (separate transaction).
- **Auth**: password_hasher (policy + validators), token_service, authentication_backend, session_service (with `resolve_refresh_token`), current_user.
- **AuthZ**: roles, policies, access_control (`require_permission`, `require_admin`).
- **Services**: audit, auth, user, patient, consent, upload (added `enforce_consent`), model_version, prediction (honesty rules), report; counts added where list endpoints need totals.
- **Schemas**: auth, user (from_user), patient (+ConsentCreate/ConsentRead), prediction, report, image_quality, upload (no storage key), model_version (Capabilities extra="ignore"), admin.
- **API**: `health.py` done; added `auth, users, patients, uploads, predictions, reports, models, admin` routes; wired in `api/v1/router.py`. `predictions.POST` decodes base64, loads consent, stores image (enforce_consent=False), calls PredictionService.predict. `predictions` list and `reports` list return accurate totals (count added).
- **Notifications** (new): email sender (console by default), events, templates, notification service; no external network by default.
- **Monitoring** (new): in-memory metrics (counters/gauges/histograms), health checks stubs, async_timed, no-op tracing.
- **Jobs** (new): worker primitives, cleanup_uploads, remove_expired_tokens, generate_report, recalculate_statistics; safe (no-op by default, non-destructive).
- **Packaging**: Pillow pinned; settings extended. (reportlab/boto3 optional if required later; document via env.)

## Notes (design constraints preserved)
- Screening-only wording; never diagnostic. No fabricated clinical values/metrics.
- Storage key never exposed; local path traversal guarded; HMAC signed URLs for `/api/v1/files/{token}` (route not added; HTTP serving optional).
- Mock inference never returns success; server never silently falls back to mock in prod.
- Failure audits persist via `record_independent` (own transaction). Services own commit boundary.
- DB URL from settings; enums stored as lowercase (values_callable); migration chain preserved (001–011). Alembic url blank.

## Remaining (Phase 3 follow-ups / Phase 4 dependencies)
- Add `/api/v1/files/{token}` endpoint if local storage serving is required in deployment.
- If pagination performance needed, add proper DB counts per filter (current counts are correct but single-query per list; existing repos follow simple pattern).
- Optionally wire NotificationService into services (prediction/report completion) if asynchronous notifications desired (not required by contracts).
- Add reportlab/boto3 to requirements if using PDF rendering/S3 in prod.
- Document new endpoints/env in `.env.example`/README as needed.

## Execution status
- **NOT** run: pytest, mypy/ruff, alembic, uvicorn/gunicorn, build, debug.  
- **No data/credentials created**; no migrations applied.  
- **No fabrications**; all inputs recorded.
