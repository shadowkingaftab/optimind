# EyeDx Configuration

Configuration templates and structure for all services. 
**No secrets are committed.** Values marked as `INPUT_REQUIRED` must be provided via environment variables or secure secret management.

## Structure
- `application/` - App-level config (API, CORS, feature flags)
- `database/` - Database connection config
- `deployment/` - Deployment-specific config
- `inference/` - Model inference config
- `logging/` - Logging config
- `model/` - Model loading/registry config
- `security/` - Auth, JWT, consent config
- `storage/` - Object storage config
- `training/` - ML training config

## Principles
- Safe defaults where possible
- Explicit absence handling (see .env.example)
- No tracked credentials or patient data
- Keys align with contracts and services
