"""Create S3 bucket on LocalStack."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.s3 import get_s3_client
from backend.config import S3_BUCKET_NAME


def create_bucket():
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Bucket {S3_BUCKET_NAME} already exists.")
    except Exception:
        client.create_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Created bucket: {S3_BUCKET_NAME}")


if __name__ == "__main__":
    create_bucket()
