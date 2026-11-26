# Tasks

## 1. Project Scaffolding & Environment

- [x] 1.1 Create `.env.example` with default connection parameters and credentials for MinIO and ClickHouse, verifying all necessary environment variables are documented.
- [x] 1.2 Create `docker-compose.yml` defining the network, volume storage, and MinIO service with health check, verifying syntax with `docker compose config`.

## 2. S3 Object Storage & Test Data Generator

- [x] 2.1 Implement synthetic order data generation script and S3 upload routine under `scripts/generate_orders.py` or shell/init script, verifying JSON format and required fields (order_id, user_id, order_date, status, total_amount).
- [x] 2.2 Configure the automated S3 bucket provisioning and seed service (`minio-init`) in `docker-compose.yml`, verifying that the bucket `warehouse-raw` and sample orders objects are staged on startup.

## 3. DWH Core Engine & Schema Initialization

- [x] 3.1 Create ClickHouse schema initialization scripts in `initdb/01_init_orders.sql` defining database `dwh`, external table `dwh.orders_s3`, and local table `dwh.orders`, verifying SQL syntax.
- [x] 3.2 Add ClickHouse service to `docker-compose.yml` with health check and initialization volume mounts, verifying full compose specification via `docker compose config`.

## 4. End-to-End Verification & Documentation

- [x] 4.1 Implement verification script `scripts/verify_setup.sh` that checks MinIO bucket contents and runs analytical SQL queries against ClickHouse to verify S3 order queries.
- [x] 4.2 Document instructions for starting the environment, accessing MinIO console, and executing analytical queries in `README.md`.

