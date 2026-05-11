from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


class StorageServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class StoredUpload:
    stored_filename: str
    storage_path: str
    storage_key: str | None
    storage_url: str | None
    file_size_bytes: int


async def save_upload(file: UploadFile, user_id: str) -> StoredUpload:
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Only PDF and DOCX files are supported.")

    file_extension = Path(file.filename or "").suffix.lower().replace(".", "")
    expected_extension = ALLOWED_CONTENT_TYPES[content_type]
    if file_extension != expected_extension:
        raise ValueError("File extension does not match the uploaded content type.")

    upload_root = Path(settings.upload_dir)
    user_folder = upload_root / user_id
    user_folder.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}.{expected_extension}"
    destination = user_folder / stored_filename

    size = 0
    with destination.open("wb") as output:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.max_file_size_mb * 1024 * 1024:
                output.close()
                destination.unlink(missing_ok=True)
                raise ValueError(f"File exceeds {settings.max_file_size_mb} MB limit.")
            output.write(chunk)

    storage_key = None
    storage_url = None

    if settings.r2_is_configured:
        storage_key = _build_r2_object_key(user_id=user_id, stored_filename=stored_filename)
        try:
            await asyncio.to_thread(
                _upload_file_to_r2,
                source_path=destination,
                object_key=storage_key,
                content_type=content_type,
            )
            storage_url = _build_r2_public_url(storage_key)
            logger.info(
                "event=r2_upload_success storage_key=%s file_size_bytes=%s user_id=%s",
                storage_key,
                size,
                user_id,
            )
        except Exception as exc:
            logger.warning(
                "event=r2_upload_failure storage_key=%s user_id=%s error=%s fallback=local",
                storage_key,
                user_id,
                exc,
            )
            storage_key = None
            storage_url = None
    else:
        logger.info(
            "event=r2_not_configured user_id=%s storage=local_only",
            user_id,
        )

    return StoredUpload(
        stored_filename=stored_filename,
        storage_path=os.fspath(destination),
        storage_key=storage_key,
        storage_url=storage_url,
        file_size_bytes=size,
    )


def _build_r2_object_key(user_id: str, stored_filename: str) -> str:
    prefix = settings.r2_key_prefix.strip().strip("/")
    if prefix:
        return f"{prefix}/{user_id}/{stored_filename}"
    return f"{user_id}/{stored_filename}"


def _build_r2_public_url(object_key: str) -> str:
    base_url = settings.r2_public_base_url.strip().rstrip("/")
    if base_url:
        return f"{base_url}/{object_key}"

    endpoint_url = settings.r2_endpoint_url.strip().rstrip("/")
    bucket_name = settings.r2_bucket_name.strip()
    if endpoint_url and bucket_name:
        return f"{endpoint_url}/{bucket_name}/{object_key}"

    return object_key


def _upload_file_to_r2(source_path: Path, object_key: str, content_type: str) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise StorageServiceError(
            "Cloud storage dependency is missing. Install `boto3` to enable Cloudflare R2 uploads."
        ) from exc

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=settings.r2_bucket_region,
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
    )

    with source_path.open("rb") as file_handle:
        client.upload_fileobj(
            Fileobj=file_handle,
            Bucket=settings.r2_bucket_name,
            Key=object_key,
            ExtraArgs={"ContentType": content_type},
        )
