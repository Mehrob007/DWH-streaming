# Proposal: Streaming DWH with Kafka, Spark Structured Streaming, RustFS, and Superset

## Why

The reference implementation in `test-DWH` executes batch ETL processing via Airflow once per day (`@daily`), which introduces significant data latency and lacks real-time visibility. To enable continuous streaming analytics, the DWH platform must process order events in real time using a streaming message broker, Spark Structured Streaming, RustFS S3 storage, ClickHouse, and Superset for visual dashboards.

## What Changes

- **Kafka / Redpanda Broker**: Introduce a high-performance, lightweight Kafka-compatible streaming broker (Redpanda) to ingest order event streams.
- **Spark Structured Streaming Engine**: Build and deploy an Apache Spark Structured Streaming service reading continuous events from Kafka, performing real-time data cleaning, deduplication, and writing micro-batches into ClickHouse.
- **S3 Storage Migration (RustFS)**: Replace MinIO with RustFS (matching `test-DWH`), serving S3 API on port 9002 and Web Console on port 9001, providing S3 bucket `bronze` for raw archival.
- **Streaming Data Generator**: Implement a continuous order producer that publishes real-time JSON order transactions into the Kafka topic.
- **Apache Superset Integration**: Add an Apache Superset service on port 8088 with ClickHouse driver installed and automated admin bootstrap for dashboards.
- **ClickHouse Schema Refinement**: Ensure the ClickHouse tables and schemas support continuous concurrent inserts and streaming aggregations.

## Capabilities

### New Capabilities

- `streaming-pipeline`: Real-time streaming pipeline using Kafka broker and Apache Spark Structured Streaming for continuous ingestion, schema validation, and ClickHouse micro-batch loading.
- `bi-visualization`: Apache Superset service providing real-time data exploration and interactive dashboards connected to ClickHouse.

### Modified Capabilities

- `s3-storage`: Migrate S3 backend to RustFS with ports 9002 (API) and 9001 (Web UI) and bucket `bronze`.
- `test-data-generator`: Transform the data generator into an ongoing streaming producer publishing to Kafka.

## Impact

- **Docker Compose**: Complete update of `docker-compose.yml` to orchestrate Redpanda, Spark streaming worker, RustFS, ClickHouse, and Superset.
- **Dockerfiles**: Add `Dockerfile.spark` and `Dockerfile` (Superset) with ClickHouse connectors.
- **Data Flow**: Shifts latency from 24 hours to sub-second / micro-batch intervals.

