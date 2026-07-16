from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings


class StorageNotConfigured(RuntimeError):
    pass


def ensure_storage_configured() -> None:
    missing = [name for name in ["S3_BUCKET", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY"] if not getattr(settings, name)]
    if missing:
        raise StorageNotConfigured(f"S3-compatible storage is not configured. Missing: {', '.join(missing)}")


def s3_client():
    ensure_storage_configured()
    import boto3

    return boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )


def build_object_key(owner_id: str, purpose: str, filename: str) -> str:
    safe_name = "".join(ch if ch.isalnum() or ch in {".", "-", "_"} else "-" for ch in filename).strip("-") or "upload.bin"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{purpose}/{owner_id}/{timestamp}-{uuid4().hex}-{safe_name}"


def public_url_for_key(object_key: str) -> str:
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{object_key}"
    if settings.S3_ENDPOINT_URL:
        return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET}/{object_key}"
    return f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{object_key}"


def create_presigned_upload(owner_id: str, purpose: str, filename: str, content_type: str) -> dict:
    object_key = build_object_key(owner_id, purpose, filename)
    client = s3_client()
    upload_url = client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": object_key, "ContentType": content_type},
        ExpiresIn=900,
    )
    return {"object_key": object_key, "upload_url": upload_url, "url": public_url_for_key(object_key)}
