"""
S3 client for document storage. Connects to LocalStack — no real AWS.
"""

import boto3
from backend.config import S3_ENDPOINT_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    return _s3_client


def upload_file(file_bytes: bytes, key: str, content_type: str) -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{S3_BUCKET_NAME}/{key}"


def download_file(key: str) -> bytes:
    client = get_s3_client()
    response = client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    return response["Body"].read()
