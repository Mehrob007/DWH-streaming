# Tasks

## 1. Environment & S3 (RustFS) Migration

- [x] 1.1 Update `.env.example` and `.env` with RustFS, Redpanda, ClickHouse, and Superset connection variables, verifying complete configuration.
- [x] 1.2 Reconfigure RustFS service in `docker-compose.yml` on ports 9002 (API) and 9001 (Web Console), verifying configuration with `docker compose config`.

## 2. Streaming Broker & Order Producer

- [x] 2.1 Add Redpanda (Kafka API) service to `docker-compose.yml` on port 9092, verifying configuration with `docker compose config`.
- [x] 2.2 Implement continuous order streaming producer `scripts/stream_producer.py` supporting both Kafka event publishing and raw S3 archival, verifying event payload generation.

## 3. ClickHouse & Superset Setup

- [x] 3.1 Update ClickHouse initialization script `initdb/01_init_sales.sql` defining database `sales` and table `sales.orders_clean` matching `test-DWH`, verifying SQL syntax.
- [x] 3.2 Create `Dockerfile` for Superset with ClickHouse driver and add `superset` service to `docker-compose.yml` on port 8088, verifying configuration with `docker compose config`.

## 4. Spark Structured Streaming Engine

- [x] 4.1 Create `Dockerfile.spark` installing Python dependencies (`clickhouse-connect`) and implement PySpark streaming job `spark/streaming_orders.py` reading from Kafka and writing micro-batches to ClickHouse.
- [x] 4.2 Add `spark` streaming service to `docker-compose.yml` running the Structured Streaming pipeline, verifying compose configuration with `docker compose config`.

## 5. End-to-End Verification & Documentation

- [x] 5.1 Implement streaming verification script `scripts/verify_streaming.sh` that checks message publishing to Kafka, Spark micro-batch processing, and ClickHouse row count growth.
- [x] 5.2 Document the streaming architecture, service ports, quickstart, and dashboard access in `README.md`.

