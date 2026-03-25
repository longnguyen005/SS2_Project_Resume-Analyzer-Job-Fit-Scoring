from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


async def save_upload(file: UploadFile, user_id: str) -> tuple[str, str, int]:
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

    return stored_filename, os.fspath(destination), size
