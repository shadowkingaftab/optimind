# Storage Configuration

Object/file storage for images, artifacts, reports.
- STORAGE_TYPE: local/s3 (default: local)
- STORAGE_PATH: INPUT_REQUIRED when local (format: absolute path)
- S3_BUCKET: INPUT_REQUIRED if s3
- S3_REGION: INPUT_REQUIRED if s3
- S3_ENDPOINT_URL: optional (for minio)
- S3_ACCESS_KEY_ID: INPUT_REQUIRED if s3 (secret)
- S3_SECRET_ACCESS_KEY: INPUT_REQUIRED if s3 (secret)

**Security**: Signed URLs for access; no public write. Never log keys.
**Retention**: Governed (see monitoring/retention). 
**Consuming**: backend/app/services/storage.py, model artifacts
**Owner**: Infra
