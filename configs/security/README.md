# Security Configuration

Auth, JWT, consent configuration.
- JWT_SECRET_KEY: INPUT_REQUIRED (format: secure random string, min 32 chars) - store in secret manager
- JWT_ALGORITHM: HS256 or RS256 (default: HS256)
- JWT_EXPIRATION_MINUTES: INPUT_REQUIRED (format: integer, positive)
- CONSENT_REQUIRED: true (default)
- PASSWORD_POLICY: documented per deployment

**Critical**: JWT_SECRET_KEY must never be committed. Absence causes startup failure with explicit message.
**Consuming**: backend/app/core/security.py, auth middleware
**Owner**: Security lead
