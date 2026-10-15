# Application Configuration

Input requirements and structure documented.
- API_HOST: INPUT_REQUIRED (format: hostname/IP)
- API_PORT: INPUT_REQUIRED (format: integer 1024-65535)  
- API_VERSION: v1 (default)
- CORS_ORIGINS: INPUT_REQUIRED (format: comma-separated URLs)
- FEATURE_FLAGS: configurable, safe defaults

**Safe absence handling**: Service must fail fast with clear error if required values missing.
**Consuming**: backend/app/core/settings.py, frontend/.env (future phases)
**Security**: No secrets in this config.
