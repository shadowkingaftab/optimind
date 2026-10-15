# Deployment config README
# Deployment definitions and requirements

## Environments
- development: local only
- staging: INPUT_REQUIRED (staging env details)
- production: INPUT_REQUIRED (production env details)

## Requirements
- All secrets via environment/secret manager
- No hardcoded credentials
- Domains/TLS: INPUT_REQUIRED (owner)
- Cloud resources: INPUT_REQUIRED (infra owner)
- Resource limits: INPUT_REQUIRED per env

## Notes
Manifests (docker-compose, k8s, terraform) defined in deployment/ (Phase 10 scope). This phase documents structure only.
No execution, no deployment performed.
