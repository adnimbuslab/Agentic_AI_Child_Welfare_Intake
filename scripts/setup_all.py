"""One-shot setup: create DynamoDB tables + S3 bucket on LocalStack."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.create_tables import create_tables
from scripts.setup_s3 import create_bucket


def main():
    print("=== Setting up LocalStack resources ===")
    print("\n--- DynamoDB Tables ---")
    create_tables()
    print("\n--- S3 Bucket ---")
    create_bucket()
    print("\n=== Setup complete ===")


if __name__ == "__main__":
    main()
