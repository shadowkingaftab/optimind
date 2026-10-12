# EyeDx AI — Vision and Phase-by-Phase Implementation Plan

## Vision

EyeDx is an AI-assisted ocular image screening platform. An authorized user submits an eye image; the system validates it, prepares it for inference, obtains a model result, presents uncertainty and an explanation when supported, and provides history and reports. It consists of a web client, application API, separately deployable model service, data/ML tools, and operating infrastructure. These layers must agree on image formats, identifiers, prediction fields and states, errors, authentication, model versions, and consent. Shared definitions belong in contracts/.

This is screening and research software. Never describe output as diagnosis, invent clinical performance, or present an unvalidated model as clinically safe. If approved data, model weights, or clinical decisions are missing, implement safe absence handling and record exactly what a person must provide. Never fabricate inputs.

## How to use this plan

Run one phase at a time. Give the implementing AI this README and the repository. Review the phase file-disposition ledger before proceeding. Do not combine phases into a single prompt.

An initial scan found 820 whitespace-only non-marker files. Treat that as a baseline, not a permanent inventory: inspect the current tree at each phase and preserve useful work already present.

### Implementation-first rules

- Phases 1–12 fill implementation. Do not run tests, debug, benchmark, tune model performance, or claim execution-based verification.
- Never write fake patient data, clinical results, credentials, model weights, dataset records, or secrets.
- For unavailable external inputs, implement safe absence handling and record exact name, format/schema, source/owner, secure delivery location, consuming files, and blocked behavior.
- Imports, placeholder classes, TODOs, hard-coded success responses, and unconnected UI do not count as implementation.
- Keep changes within phase except a necessary small interface adjustment; record dependencies.
- Do not delete files or change their purpose to simplify the ledger. Preserve .gitkeep markers.
- No deployment, publication, external messaging, or production activation.

### Required file disposition

Every non-marker file must be marked:
1. **Implemented** — useful implementation/configuration/documentation or reproducible generation logic is present and connected.
2. **Input required** — code handles absence safely where possible; exact external input is recorded.
3. **Intentionally non-code** — e.g. license, generated lockfile, data marker or externally supplied binary, with supply method.
4. **Deferred by scope** — test files only, until Phase 13.

No file may be “not looked at.” A phase is complete when every scoped file has a disposition and no unexplained blank, placeholder-only body, or disconnected stub remains. This is a source review condition, not execution verification.

## Intended product flow

~~~text
Browser
  └─ Frontend: sign-in, upload, progress, results, explanation, history, reports
       └─ Backend: identity, authorization, consent, upload, persistence, audit, orchestration
            ├─ Database/storage: users, consent, images, predictions, reports, versions, audit
            └─ Model service: quality, preprocessing, versioned inference, uncertainty, explanation
                 └─ ML package: governed data, training/evaluation, calibration, export, metadata
Operations: configuration, containers, migrations, deployment, logs, metrics, alerts, drift, recovery
Contracts: JSON schemas, OpenAPI, examples, shared errors and prediction shapes
~~~

End-to-end lifecycle: authenticate and authorize; enforce consent; validate and sanitize image; reject unusable quality without a disease result; create traceable request; call configured model service; return model version, supported labels, uncertainty/abstention and explanation availability; persist status/audit; show screening limitations; represent failures as failures.

## Phase map

| Phase | Scope | Outcome |
|---|---|---|
| 1 | Contracts, configs, root conventions | Stable interfaces |
| 2 | Backend foundation and persistence | Startup, settings, database, models, middleware |
| 3 | Backend workflows | Auth, upload, predictions, reports, audit, jobs |
| 4 | Dataset governance and ML input | Reproducible data preparation |
| 5 | ML models, training, evaluation, export | Implemented workflow with honest evidence boundaries |
| 6 | Model service | Versioned inference connected to contracts |
| 7 | Frontend foundation | Routes, API, state, layouts, accessible shared UI |
| 8 | Frontend workflows | Connected user screens |
| 9 | Model registry | Provenance, promotion, rollback |
| 10 | Deployment | Local, staging, production definitions |
| 11 | Monitoring and maintenance | Privacy-safe telemetry, alerts, backup/recovery |
| 12 | Docs, research, remaining files | Accurate guidance and input register |
| 13 | Test source only | Populate tests; do not execute |

# Ready-to-paste phase prompts

Each prompt is a separate task. Inspect every scoped file, preserve useful content, and disposition every file.

## Phase 1 — Contracts and root conventions

**Scope:** contracts/**, configs/**, root .env.example, package.json, pyproject.toml, requirements.txt, .editorconfig, .gitignore, .dockerignore, .pre-commit-config.yaml, Makefile.

~~~text
Implement Phase 1 from README. Inspect every scoped file and the tree. Make contracts the shared source of truth. Define consistent API versioning, request/response shapes, prediction states, model metadata, uncertainty/abstention, pagination, auth expectations and structured errors. Align JSON schemas, OpenAPI and examples. Add documented safe configuration defaults without tracked secrets. Keep root Python and JavaScript metadata consistent with subprojects. Never invent clinical values or credentials. Do not run tests, linters, builds or debug. Do not implement later business features. Report each scoped file as Implemented, Input required or Intentionally non-code, with reason and dependency.
~~~

## Phase 2 — Backend foundation

**Scope:** backend/app/core, config, database, models, exceptions, middleware; common/error/pagination schemas; main.py, lifespan.py, routers; migrations, Alembic config, backend packaging, requirements, Dockerfile, Gunicorn config, .env.example.

~~~text
Implement Phase 2 from README. Inspect the backend and Phase 1 contracts. Implement startup/shutdown, typed settings, database engine/session/base, declared models/relationships, migration environment and migration files, exception handling, request IDs, privacy-safe logging, security headers, CORS and configured rate limits. Keep migrations consistent with models and support configured PostgreSQL. Make missing configuration errors explicit; never log credentials or health data. Do not duplicate API schemas. Do not run migrations, tests, formatters, servers or debug. Do not implement Phase 3 endpoints. Disposition every file and record external inputs/dependencies.
~~~

## Phase 3 — Backend workflows

**Scope:** remaining backend/app including authentication, authorization, API v1, schemas, repositories, services, preprocessing, storage, inference, postprocessing, explainability, reports, notifications, audit, monitoring, jobs and utilities; backend/README.md. Backend tests belong to Phase 13.

~~~text
Implement Phase 3 from README. Inspect every backend source file and Phases 1–2. Complete auth/session, roles, users, patients/consent, upload validation/quarantine, image quality, prediction submission/status/history, model info, reports/downloads, audit and health. Connect routes, schemas, services and repositories. Implement safe storage, configured signed access, inference timeout/retry/circuit breaker, uncertainty/abstention mapping and honest unavailable states. Use transactions/idempotency where retries could duplicate records. Implement safe retention jobs. Never hard-code a successful prediction. Keep medical wording within screening support. Do not run tests, migrations, servers, linters or debug. Leave tests for Phase 13. Disposition every non-test file and name required service/clinical inputs.
~~~

## Phase 4 — Dataset and ML input pipeline

**Scope:** datasets/** except markers; ML data, preprocessing, augmentation, utilities; ml/data/**, data configs/scripts, docs/datasets/**.

~~~text
Implement Phase 4 from README. Inspect dataset tree, ML input code and contracts. Implement reproducible ingestion, manifest/metadata validation, label mapping, duplicate/leakage checks, patient-level splits, decoding, quality checks, preprocessing/augmentation config, statistics and provenance. Do not download, invent, relabel or commit patient images. Make licensed data configurable and fail clearly when absent. Preserve patient-level separation and source/licence/consent provenance. Keep raw/interim/processed boundaries explicit and never log private data. Populate DVC and dataset docs with reproducible logic or exact input requests. Do not execute pipelines, downloads, tests or debug. Disposition every file including data placeholders.
~~~

## Phase 5 — ML models and export

**Scope:** ml/src/eyedx_ml models, training, metrics, evaluation, calibration, explainability, export, inference, registry; remaining ML configs/scripts, ml/models, ml/notebooks, docs/model, model configs.

~~~text
Implement Phase 5 from README. Inspect ML package, data pipeline, contracts and configs. Implement declared architectures, losses, training orchestration, checkpoint metadata, reproducibility controls, metric calculations, subgroup reporting hooks, calibration, uncertainty/abstention, explanations and export. Use only approved labels. If labels, pretrained weights, GPU or validation cohorts are unavailable, implement configurable loading and safe unavailable states; record exact inputs. Never invent weights, metrics, clinical thresholds or notebook findings. Export model version, preprocessing, labels and calibration metadata. Do not train, evaluate, benchmark, execute notebooks, test or debug. Disposition every file and state real inputs required.
~~~

## Phase 6 — Model service

**Scope:** model_service/app, artifacts, README, packaging, requirements, Dockerfile and .env.example. Tests belong to Phase 13.

~~~text
Implement Phase 6 from README. Inspect service tree, contracts and Phase 5 interfaces. Implement lifecycle, settings, health/model-info/explain/quality/predict APIs, validation, model/label/calibration/threshold loaders, preprocessing, inference, decoding, postprocessing, uncertainty, explanations and safe metrics. Make loading explicit/versioned; report unavailable or fail readiness if approved artifacts are absent. Enforce file/tensor limits and timeouts. Never log raw images or sensitive payloads. Keep responses compatible with backend/contracts. Never invent a model or return fake predictions. Do not run tests, benchmarks, load models, start servers or debug. Leave tests for Phase 13. Disposition every file and list exact artifact inputs.
~~~

## Phase 7 — Frontend foundation

**Scope:** frontend/src app, api, services, context, store, routes, layouts, types, constants, utils, hooks, styles, validation, common/layout/navigation components; index.html and tooling/config.

~~~text
Implement Phase 7 from README. Inspect frontend and contracts. Build TypeScript app foundation: typed environment config, API client/error handling, auth/session state, guarded routes, layouts, navigation, state conventions, validation, accessible shared UI, loading/empty/error states and responsive tokens. Use existing framework/dependencies. Align API types with contracts. Handle expired sessions, network and validation errors. No secrets in frontend config or invented success responses. Avoid unnecessary health-data storage. Use plain-language screening content. Do not install packages or run tests, builds, lint or debug. Disposition every file and record dependencies.
~~~

## Phase 8 — Frontend workflows

**Scope:** remaining frontend pages/components (admin, analysis, auth, prediction, reports, upload), assets and public files. Tests/configs belong to Phase 13.

~~~text
Implement Phase 8 from README. Inspect remaining frontend files and Phase 7. Complete sign-in/recovery, dashboard, upload/validation/progress, quality rejection, prediction progress, results/uncertainty/explanation, patient/history, report preview/download, profile/settings, consent and authorized admin workflows. Connect screens to API and implement loading, empty, success, partial, unavailable and error states. Ensure keyboard access, labels, responsive layout and clear medical limitations. Never show fabricated predictions, patients, reports, heatmaps or clinical claims. For absent endpoint/assets, show unavailable state and record dependency; do not add arbitrary eye imagery. Do not run tests, builds, visual automation or debug. Disposition every production file.
~~~

## Phase 9 — Model registry

**Scope:** model_registry/** except markers, ML registry integration and model registry docs.

~~~text
Implement Phase 9 from README. Inspect registry and Phase 5 metadata. Implement immutable versions, checksums/locations, training/data provenance, labels, preprocessing/calibration metadata, validation evidence references, benchmark records, promotion, active version and rollback history. Define acceptance gates without inventing clinical thresholds; an approved owner/evidence must supply them. Do not commit model binaries, patient data, fake cards or validation records. Prevent unapproved artifacts becoming active. Fill templates with required evidence fields. Do not run validators, load models, test or debug. Disposition every file and list operator-supplied evidence/artifacts.
~~~

## Phase 10 — Deployment

**Scope:** deployment/**, docker-compose*.yml, Dockerfiles, .github/workflows/**, Dependabot/CODEOWNERS, deployment-related root config.

~~~text
Implement Phase 10 from README. Inspect deployment manifests and service configuration. Provide coherent local, staging and production definitions for frontend, backend, model service, database, storage and proxy. Wire health/readiness, networks, volumes, config boundaries, migration steps, TLS assumptions, secret references and least privilege. CI describes automation but is not run. Kubernetes/Terraform use variables and safe defaults, never real secrets or pretend cloud IDs. Align ports/routes/environment keys with applications. Do not deploy, build, apply infrastructure, run CI, test or debug. Disposition every file and list credentials, domains, cloud decisions and owners required.
~~~

## Phase 11 — Monitoring and maintenance

**Scope:** monitoring/**, scripts/maintenance/**, scripts/database/**, storage/** except markers, backend audit/monitoring modules, docs/security/**.

~~~text
Implement Phase 11 from README. Inspect monitoring, storage, audit and maintenance together. Implement privacy-safe logs, metrics, tracing hooks, latency/error dashboards, alerts, drift inputs, retention, cleanup, backup/restore and artifact verification. Align metric names; never use patient IDs, images, tokens or health data in labels/logs. Make thresholds configurable or identify the owner. Enforce retention/authorization for quarantine, temp files and reports. Require explicit targets/config for destructive scripts. Do not run scripts, connect to infrastructure, test, benchmark or debug. Disposition every file and identify operational inputs/owners.
~~~

## Phase 12 — Documentation and remaining files

**Scope:** docs/**, research/**, assets/**, root/service READMEs, governance docs, setup/development/deployment/training/evaluation/export/dataset/testing scripts, remaining configs and every unassigned file.

~~~text
Implement Phase 12 from README. Inventory every file not assigned earlier plus docs, research and assets. Write accurate user, developer, ML, API, privacy, security, clinical-limitations, architecture, data-governance, model-lifecycle, deployment, recovery and operations guidance from actual code/contracts. Correct claims of testing, performance, approval or deployment unless evidence exists. Research must be sourced; otherwise make templates and exact input requests, never fabricated results. Make scripts useful and config-consistent without executing them. Preserve supplied legal text and request review where needed. Disposition every file; none may remain unassigned. Do not run scripts, tests, builds, deployment or debug.
~~~

## Phase 13 — Test source only, no execution

**Scope:** backend/tests, frontend/tests, ml/tests, model_service/tests, root tests; contract, integration, end-to-end, performance, resilience and security suites.

~~~text
Implement Phase 13 from README after implementation. Inspect implemented modules/contracts and author meaningful test source for existing scenarios. Cover success and safe failure/uncertainty with mocks and synthetic fixtures only. Never include real patient data, credentials, fake clinical ground truth or passing claims. Make external services/cost explicit. Do not execute tests, collect coverage, debug, install dependencies or change production modules except a narrowly essential interface correction recorded for review. Disposition every test file and mark all suites NOT RUN.
~~~

## Complete repository ownership map

Phase prompts include descendants unless stated otherwise.

- Root governance/build files and README: Phases 1, 10, 12.
- contracts/** and configs/**: Phase 1; all phases consume contracts.
- backend/app/**, migrations and packaging: Phases 2–3; backend tests Phase 13.
- datasets/** and ml/**: Phases 4–5; ML tests Phase 13. Outputs/checkpoints need approved generation inputs.
- model_service/**: Phase 6 except tests in Phase 13.
- frontend/**: Phases 7–8 except tests and test-runner configs in Phase 13.
- model_registry/**: Phase 9.
- deployment/**, monitoring/**, storage/**, compose, CI and operations scripts: Phases 10–11.
- docs/**, research/**, assets/**, remaining scripts/service READMEs: Phase 12 unless assigned earlier.
- root tests/** and service test directories: Phase 13.
- .gitkeep: intentional marker.

## Inputs never to fabricate

Track exact request and owner/source for each missing item:
- **Clinical task:** image modalities, intended population/use, supported diseases/labels, exclusions, referral wording, clinical owner approval.
- **Data:** licensed access, image/label manifests, patient-level split identifiers, consent/provenance, retention/de-identification rules.
- **Model evidence:** approved weights, preprocessing/labels, calibration, validation cohorts, subgroup evidence, acceptance criteria, model card and approval.
- **Runtime:** database URL, object storage, mail, auth/session secrets, signing keys, telemetry, artifact location and service domains.
- **Operations:** cloud/account/region, TLS/domain owner, deployment identities, backup target/retention, alert recipients, SRE owner and resource limits.
- **Legal/privacy:** jurisdiction, data-processing terms, retention obligations, incident contact and regulatory review.
- **Product/brand:** approved identity assets, languages, accessibility requirements and product decisions.

For each input record name, format/schema, supplier, secure delivery location, consuming modules and safe behavior while absent. Never put secret values or identifiable data in this README or source control.

## Phase completion record

Append after each phase. Do not imply execution verification.

~~~text
### Phase N — YYYY-MM-DD
- Implemented paths:
- Input-required paths/items: exact input, owner/source, format and blocked behavior
- Intentionally non-code paths:
- Deferred paths: test files only before Phase 13
- Cross-phase dependency:
- Execution status: NOT RUN — no tests, builds, debugging or deployment
~~~

## Final completion checklist

- [ ] Every non-marker file has implementation or explicit input/non-code disposition.
- [ ] API boundaries use shared contracts.
- [ ] Upload, quality rejection, inference, uncertainty, persistence, reports and failures form one workflow.
- [ ] Frontend connects to real API behavior and presents unavailable/error states honestly.
- [ ] Missing data/model is explicit; no fabricated images, labels, weights, metrics or clinical claims.
- [ ] Every configuration key has a consumer and safe absence behavior.
- [ ] Deployment, monitoring, backup and recovery match implemented services.
- [ ] Test source is populated in Phase 13; suites remain NOT RUN in this iteration.
- [ ] Every external input has exact request, owner/source, format and consuming module.
- [ ] No file is an unexplained blank, placeholder, disconnected stub or “not reviewed.”
