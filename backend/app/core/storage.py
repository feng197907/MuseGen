"""MinIO / S3-compatible object storage client."""
import uuid
import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from app.core.config import settings

_s3_client: BaseClient | None = None


def get_storage_client() -> BaseClient:
    """Return a singleton boto3 S3 client configured for MinIO."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        # Ensure bucket exists
        try:
            _s3_client.head_bucket(Bucket=settings.S3_BUCKET)
        except ClientError:
            _s3_client.create_bucket(Bucket=settings.S3_BUCKET)
    return _s3_client


def upload_file(
    local_path: str,
    project_id: str,
    asset_type: str,
    extension: str,
) -> str:
    """Upload a file to S3 and return the public object URL.

    Args:
        local_path: Local file path to upload.
        project_id: Project UUID for key namespacing.
        asset_type: Asset category (e.g. 'keyframe', 'audio', 'video').
        extension: File extension without leading dot.

    Returns:
        Public URL string of the uploaded object.
    """
    key = f"{project_id}/{asset_type}/{uuid.uuid4()}.{extension}"
    client = get_storage_client()
    client.upload_file(
        local_path,
        settings.S3_BUCKET,
        key,
        ExtraArgs={"ACL": "public-read"},
    )
    return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"


def upload_bytes(
    data: bytes,
    project_id: str,
    asset_type: str,
    extension: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload raw bytes to S3 and return the public URL."""
    key = f"{project_id}/{asset_type}/{uuid.uuid4()}.{extension}"
    client = get_storage_client()
    import io
    client.upload_fileobj(
        io.BytesIO(data),
        settings.S3_BUCKET,
        key,
        ExtraArgs={"ACL": "public-read", "ContentType": content_type},
    )
    return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"
