import os
from dotenv import load_dotenv

load_dotenv(override=True)

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", LOCALSTACK_ENDPOINT)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", LOCALSTACK_ENDPOINT)
LAMBDA_ENDPOINT_URL = os.getenv("LAMBDA_ENDPOINT_URL", LOCALSTACK_ENDPOINT)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "claude-opus-4-7")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "child-welfare-intake-docs")

CONFIDENCE_THRESHOLD_INTAKE = float(os.getenv("CONFIDENCE_THRESHOLD_INTAKE", "0.3"))
CONFIDENCE_THRESHOLD_RISK = float(os.getenv("CONFIDENCE_THRESHOLD_RISK", "0.6"))
CONFIDENCE_THRESHOLD_BIAS = float(os.getenv("CONFIDENCE_THRESHOLD_BIAS", "0.7"))
DATA_QUALITY_THRESHOLD = float(os.getenv("DATA_QUALITY_THRESHOLD", "0.5"))
MAX_FOLLOWUP_ROUNDS = int(os.getenv("MAX_FOLLOWUP_ROUNDS", "5"))

DYNAMODB_TABLES = {
    "IntakeCases": {
        "TableName": "IntakeCases",
        "KeySchema": [{"AttributeName": "caseId", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "caseId", "AttributeType": "S"}],
    },
    "IntakeMessages": {
        "TableName": "IntakeMessages",
        "KeySchema": [
            {"AttributeName": "caseId", "KeyType": "HASH"},
            {"AttributeName": "messageTimestamp", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "caseId", "AttributeType": "S"},
            {"AttributeName": "messageTimestamp", "AttributeType": "S"},
        ],
    },
    "IntakeDocuments": {
        "TableName": "IntakeDocuments",
        "KeySchema": [
            {"AttributeName": "caseId", "KeyType": "HASH"},
            {"AttributeName": "documentId", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "caseId", "AttributeType": "S"},
            {"AttributeName": "documentId", "AttributeType": "S"},
        ],
    },
    "AgentOutputs": {
        "TableName": "AgentOutputs",
        "KeySchema": [
            {"AttributeName": "caseId", "KeyType": "HASH"},
            {"AttributeName": "agentNameTimestamp", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "caseId", "AttributeType": "S"},
            {"AttributeName": "agentNameTimestamp", "AttributeType": "S"},
        ],
    },
    "AuditEvents": {
        "TableName": "AuditEvents",
        "KeySchema": [
            {"AttributeName": "caseId", "KeyType": "HASH"},
            {"AttributeName": "eventTimestamp", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "caseId", "AttributeType": "S"},
            {"AttributeName": "eventTimestamp", "AttributeType": "S"},
        ],
    },
}
