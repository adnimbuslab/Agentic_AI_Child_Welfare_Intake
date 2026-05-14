"""
DynamoDB client shared across all MCP servers and lambdas.
Connects to LocalStack — no real AWS.
"""

from decimal import Decimal
import boto3
from backend.config import DYNAMODB_ENDPOINT_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

_dynamodb_resource = None
_dynamodb_client = None


def get_dynamodb_resource():
    global _dynamodb_resource
    if _dynamodb_resource is None:
        _dynamodb_resource = boto3.resource(
            "dynamodb",
            endpoint_url=DYNAMODB_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    return _dynamodb_resource


def get_dynamodb_client():
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = boto3.client(
            "dynamodb",
            endpoint_url=DYNAMODB_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    return _dynamodb_client


def get_table(table_name: str):
    return get_dynamodb_resource().Table(table_name)


def sanitize_for_dynamo(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: sanitize_for_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_dynamo(i) for i in obj]
    return obj


def deserialize_from_dynamo(obj):
    """Convert Decimal values back to float/int when reading from DynamoDB."""
    if isinstance(obj, Decimal):
        if obj == int(obj):
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: deserialize_from_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deserialize_from_dynamo(i) for i in obj]
    return obj
