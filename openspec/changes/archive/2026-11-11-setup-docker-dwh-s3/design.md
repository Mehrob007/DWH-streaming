# Design: Docker Compose DWH with MinIO S3 and Test Orders

## Context

The repository is newly initialized for DWH streaming development. To build and test streaming transformations and analytical queries locally, developers need a self-contained environment with S3-compatible storage and a columnar query engine. See `proposal.md` for motivation and `specs/` for behavioral requirements.

## Goals / Non-Goals

**Goals:**
- Provide a single `docker-compose.yml` to spin up MinIO (S3), ClickHouse (DWH), and an automated data seeding container.
- Auto-provision the S3 bucket (`warehouse-raw`) and seed mock order records in NDJSON/CSV format upon container startup.
- Configure ClickHouse with pre-created databases, tables, and S3 table engines for immediate querying of S3 order files.
- Enable web UI access for MinIO console and HTTP/Native client access for ClickHouse.

**Non-Goals:**
- Production security hardening (e.g. self-signed TLS certificates, complex IAM roles); environment uses developer-friendly default credentials.
- Full streaming ingestion pipeline (e.g., Kafka / Debezium / Flink); those will be layered on top in subsequent changes.

## Decisions

### 1. Storage Engine: MinIO
- **Choice**: MinIO (`minio/minio`).
- **Rationale**: De-facto industry standard for local S3 simulation; provides high fidelity with AWS S3 APIs, high throughput, and a built-in web management console.
- **Alternatives considered**:
  - *LocalStack*: Heavyweight for S3-only use case, slower startup, fewer visual inspectability tools without pro tiers.
  - *Ceph / SeaweedFS*: Higher operational complexity.

### 2. Analytical DWH Engine: ClickHouse
- **Choice**: ClickHouse Server (`clickhouse/clickhouse-server`).
- **Rationale**: Highly optimized for columnar analytical queries and streaming architectures; natively supports `S3` table engines and `s3()` table functions out of the box with zero additional drivers.
- **Alternatives considered**:
  - *PostgreSQL*: Not columnar; poor fit for large-scale DWH streaming analytics.
  - *DuckDB*: Excellent for single-node embedded analytics, but does not run natively as a long-lived multi-client server service in Docker Compose as naturally as ClickHouse.

### 3. Data Seeding Mechanism: MinIO Client (`mc`) + Python Seed Script
- **Choice**: An ephemeral init service (`dwh-init`) running `minio/mc` or a lightweight container running a Python data generator script.
- **Rationale**: Ensures the bucket is created and populated idempotently before user queries run, without requiring manual setup steps from developers.
- **Data Model for Orders**:
  - `order_id`: String (UUID or monotonic ID)
  - `user_id`: UInt32
  - `order_date`: Date
  - `order_timestamp`: DateTime
  - `status`: String (`pending`, `completed`, `cancelled`, `refunded`)
  - `total_amount`: Float64
  - `currency`: String (e.g. `USD`, `RUB`)
  - `items_count`: UInt32

### 4. ClickHouse Schema Layout
- `dwh.orders_s3`: External S3 table reading directly from `http://minio:9000/warehouse-raw/orders/*.json`.
- `dwh.orders`: `MergeTree` local storage table partitioned by month and ordered by `(order_date, order_id)`.

## Risks / Trade-offs

- **[Risk] Startup race conditions** (ClickHouse or Init service attempting to access MinIO before it is ready)
  → *Mitigation*: Use Docker Compose `healthcheck` on MinIO (`curl -f http://localhost:9000/minio/health/live`) and `depends_on: { minio: { condition: service_healthy } }`.
- **[Risk] S3 internal vs external host routing** (ClickHouse running inside Docker network querying MinIO vs host tools querying MinIO)
  → *Mitigation*: Standardize Docker container hostname as `minio:9000` for container-to-container calls, while mapping port `9000` to `localhost:9000` for host access.

