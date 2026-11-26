# Proposal: Setup Docker Compose DWH with S3 Test Orders Storage

## Why

Currently, the repository is uninitialized and lacks a local development and testing environment for streaming DWH workflows. A containerized DWH environment with S3-compatible object storage and mock orders data is needed to enable local testing, schema experimentation, and streaming ETL development without external cloud dependencies.

## What Changes

- Add a root `docker-compose.yml` defining the core DWH stack and S3-compatible storage.
- Introduce S3-compatible object storage service (MinIO) with pre-configured access credentials, default buckets, and local web console.
- Add an automated data initialization service (or seed container/script) that populates the S3 bucket with realistic test order data (order_id, user_id, order_timestamp, status, total_amount, items).
- Introduce an analytical DWH engine (ClickHouse) integrated with S3 for direct querying and loading of orders data.
- Provide environment configuration templates (`.env.example`) and verification documentation.

## Capabilities

### New Capabilities

- `s3-storage`: S3-compatible object storage service providing bucket management, API access, and web console for local data lakehouse storage.
- `test-data-generator`: Automated generation and seeding of synthetic order transactions into S3 object storage.
- `dwh-core`: Columnar analytical DWH engine with configured schemas, tables, and native S3 table integrations for analytical queries.

### Modified Capabilities

*(None - greenfield project)*

## Impact

- **Infrastructure / Docker**: New `docker-compose.yml`, MinIO container, ClickHouse container, and init scripts.
- **Data Schemas**: Defines standard order data model (order ID, customer, line items, status, timestamp, monetary amounts).
- **Dependencies**: Docker and Docker Compose prerequisites.

