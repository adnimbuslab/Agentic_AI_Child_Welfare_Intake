# Deploy — Child Welfare Intake System

Deploy the full system to LocalStack for local development and testing.

## Steps

1. **Start LocalStack and supporting services:**
   ```
   docker-compose up -d
   ```

2. **Create DynamoDB tables** (IntakeCases, IntakeMessages, IntakeDocuments, AgentOutputs, AuditEvents):
   ```
   python scripts/create_tables.py
   ```

3. **Create S3 bucket** for document storage:
   ```
   docker exec localstack awslocal s3 mb s3://child-welfare-intake-docs
   ```

4. **Deploy Lambda functions** via LocalStack:
   ```
   python scripts/deploy_lambdas.py
   ```

5. **Configure API Gateway** routes:
   ```
   python scripts/setup_api_gateway.py
   ```

6. **Start the React frontend:**
   ```
   cd frontend && npm install && npm run dev
   ```

7. **Run smoke tests** to verify deployment:
   ```
   python -m pytest tests/test_smoke.py -v
   ```

## Environment Variables
All configuration is read from `.env` at project root. Key variables:
- `LOCALSTACK_ENDPOINT` — LocalStack endpoint (default: http://localhost:4566)
- `DYNAMODB_ENDPOINT_URL` — DynamoDB via LocalStack (default: http://localhost:4566)
- `S3_ENDPOINT_URL` — S3 via LocalStack (default: http://localhost:4566)
- `LLM_MODEL_ID` — Single-point LLM model config for ALL agents (default: claude-opus-4-7)
- `LLM_PROVIDER` — Single-point LLM provider config for ALL agents (default: anthropic)
- `ANTHROPIC_API_KEY` — API key for Claude

**No real AWS services are used.** All DynamoDB, S3, Lambda, and API Gateway run on LocalStack via Docker.

## Teardown
```
docker-compose down -v
```
