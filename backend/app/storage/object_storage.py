"""S3-compatible object storage backend.

Uses ``boto3`` lazily. When boto3 or credentials are unavailable the backend
raises an honest ``StorageUnavailableError`` rather than falling back to an
insecure local path.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from app.exceptions.storage import ObjectNotFoundError, StorageUnavailableError
from app.storage.storage_interface import StorageBackend, StoredObject
from app.utils.hashing import sha256_hex


class ObjectStorage(StorageBackend):
    """S3-compatible object storage."""

    def __init__(
        self,
        *,
        bucket: str,
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
    ) -> None:
        self._bucket = bucket
        self._region = region
        self._endpoint_url = endpoint_url
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import boto3  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise StorageUnavailableError(
                "Object storage requires the 'boto3' package."
            ) from exc

        if not self._bucket:
            raise StorageUnavailableError("S3 bucket is not configured.")

        try:
            self._client = boto3.client(
                "s3",
                region_name=self._region,
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
            )
        except Exception as exc:  # noqa: BLE001
            raise StorageUnavailableError(
                "Object storage client could not be created."
            ) from exc
        return self._client

    async def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
    ) -> StoredObject:
        client = self._get_client()

        def _put() -> None:
            client.put_object(
                Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
            )

        await asyncio.to_thread(_put)
        return StoredObject(key=key, size_bytes=len(data), checksum_sha256=sha256_hex(data))

    async def get(self, key: str) -> bytes:
        client = self._get_client()

        def _get() -> bytes:
            try:
                obj = client.get_object(Bucket=self._bucket, Key=key)
                return obj["Body"].read()
            except Exception as exc:  # noqa: BLE001
                # boto3 raises ClientError with code NoSuchKey for missing keys.
                if exc.__class__.__name__ == "ClientError":
                    raise ObjectNotFoundError() from exc
                raise

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> None:
        client = self._get_client()

        def _delete() -> None:
            client.delete_object(Bucket=self._bucket, Key=key)

        await asyncio.to_thread(_delete)

    async def exists(self, key: str) -> bool:
        client = self._get_client()

        def _head() -> bool:
            try:
                client.head_object(Bucket=self._bucket, Key=key)
                return True
            except Exception as exc:  # noqa: BLE001
                if exc.__class__.__name__ == "ClientError":
                    return False
                raise

        return await asyncio.to_thread(_head)

    async def signed_url(self, key: str, *, expires_seconds: int = 300) -> str:
        client = self._get_client()

        def _presign() -> str:
            return client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=max(1, int(expires_seconds)),
            )

        return await asyncio.to_thread(_presign)
