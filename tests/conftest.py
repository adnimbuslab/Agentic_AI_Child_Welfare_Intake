"""Shared fixtures for all test categories."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("LOCALSTACK_ENDPOINT", "http://localhost:4566")
os.environ.setdefault("DYNAMODB_ENDPOINT_URL", "http://localhost:4566")
os.environ.setdefault("S3_ENDPOINT_URL", "http://localhost:4566")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("S3_BUCKET_NAME", "child-welfare-intake-docs")

from fastapi.testclient import TestClient
from backend.api.app import app
from backend.db import get_dynamodb_client
from backend.s3 import get_s3_client
from backend.config import DYNAMODB_TABLES, S3_BUCKET_NAME


@pytest.fixture(scope="session", autouse=True)
def setup_localstack():
    client = get_dynamodb_client()
    existing = client.list_tables()["TableNames"]
    for table_name, schema in DYNAMODB_TABLES.items():
        if table_name not in existing:
            client.create_table(
                TableName=schema["TableName"],
                KeySchema=schema["KeySchema"],
                AttributeDefinitions=schema["AttributeDefinitions"],
                BillingMode="PAY_PER_REQUEST",
            )

    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=S3_BUCKET_NAME)
    except Exception:
        s3.create_bucket(Bucket=S3_BUCKET_NAME)

    yield


@pytest.fixture
def client():
    return TestClient(app)
