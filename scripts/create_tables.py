"""Create all DynamoDB tables on LocalStack."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_dynamodb_client
from backend.config import DYNAMODB_TABLES


def create_tables():
    client = get_dynamodb_client()
    existing = client.list_tables()["TableNames"]

    for table_name, schema in DYNAMODB_TABLES.items():
        if table_name in existing:
            print(f"Table {table_name} already exists, skipping.")
            continue

        client.create_table(
            TableName=schema["TableName"],
            KeySchema=schema["KeySchema"],
            AttributeDefinitions=schema["AttributeDefinitions"],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Created table: {table_name}")

    print("All tables ready.")


if __name__ == "__main__":
    create_tables()
