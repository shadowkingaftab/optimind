# EyeDx Contracts

Shared API contracts for EyeDx - JSON schemas, OpenAPI specs, and examples.

## Principles
- Screening-only; no diagnostic claims
- Consistent API versioning (v1)
- Structured errors with request_id for traceability
- Uncertainty/abstention/low_quality states represented explicitly
- Contracts are single source of truth - consumers must align to these definitions

## Structure
- `json-schemas/` - JSON Schema (draft 2020-12) definitions
- `openapi/` - OpenAPI 3.1 specifications
- `examples/` - Example payloads (non-clinical placeholders)

## Usage
Contracts define the interface between:
- Frontend ↔ Backend (backend-api.yaml)
- Backend ↔ Model Service (model-service-api.yaml)
