# Design: Streaming DWH Architecture with Kafka, Spark, ClickHouse, RustFS, and Superset

## Context

In `test-DWH`, orders were processed in daily batches via Airflow invoking `spark-submit`. This change re-architects the system into an end-to-end streaming architecture while adopting the user-requested components: Redpanda (Kafka API), Apache Spark Structured Streaming, RustFS S3, ClickHouse, and Apache Superset.

## Goals / Non-Goals

**Goals:**
- Provide sub-second to micro-batch (2-5s) end-to-end latency from event generation to ClickHouse analytical availability.
- Deploy Kafka-compatible broker (Redpanda) for high-throughput, low-latency streaming.
- Deploy Apache Spark Structured Streaming container that continuously ingests from Kafka, applies data cleaning/transformations, and writes micro-batches to ClickHouse `sales.orders_clean`.
- Deploy RustFS on port 9002 (S3 API) and 9001 (Web Console) with bucket `bronze` for raw archival.
- Deploy Apache Superset on port 8088 pre-configured with ClickHouse database connectivity.
- Provide a streaming producer script that continuously generates realistic order events with controllable velocity.

**Non-Goals:**
- Batch scheduling orchestration (Airflow is omitted because the streaming pipeline runs continuously as persistent services).
- Multi-node clustering (all services run in single-node mode optimized for local development).

## Decisions

### 1. Message Broker: Redpanda (Kafka API compatible)
- **Choice**: `redpandadata/redpanda:latest`.
- **Rationale**: 100% Kafka API compatible, starts in < 1 second, does not require JVM or Zookeeper/KRaft cluster overhead, and consumes minimal memory (< 200MB).
- **Topic**: `orders_stream`.

### 2. Stream Processing: Spark Structured Streaming
- **Choice**: PySpark script running inside the `spark` container using `spark-submit` with `--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`.
- **Ingestion Mode**: `spark.readStream.format("kafka")`.
- **Sink**: Micro-batch `writeStream.foreachBatch(...)` pushing cleaned rows to ClickHouse via `clickhouse_connect`.
- **Trigger**: `processingTime='2 seconds'`.

### 3. S3 Storage: RustFS
- **Choice**: `rustfs/rustfs:latest`.
- **Rationale**: User requested RustFS matching `test-DWH`.
- **Port Mapping**: Host port `9002` -> Container port `9000` (to avoid conflicting with ClickHouse native client port `9000`). Console on `9001`.

### 4. DWH & Schema: ClickHouse
- **Database**: `sales`.
- **Table**: `sales.orders_clean` (`order_id UInt64`, `order_date Date`, `client String`, `city String`, `amount Decimal(12,2)`, `ingested_at DateTime`).
- **Engine**: `MergeTree()`, partitioned by `toYYYYMM(order_date)` and ordered by `(order_date, order_id)`.

### 5. BI Layer: Apache Superset
- **Choice**: `apache/superset:latest` with `clickhouse-connect` driver.
- **Port**: `8088`.
- **Default Credentials**: `admin` / `admin123`.

## Risks / Trade-offs

- **[Risk] Spark Kafka dependency download latency on startup**
  → *Mitigation*: Bundle the spark-submit launch command with Maven package cache or pre-download JARs so restart is instant.
- **[Risk] Unhandled corrupt JSON payloads in streaming DataFrame**
  → *Mitigation*: Use `from_json` with permissive mode and validate non-null columns (`order_id`, `order_date`, `amount`) before insertion.
- **[Risk] Port 9000 conflict between ClickHouse native port and RustFS**
  → *Mitigation*: Map RustFS to host port `9002:9000` while ClickHouse occupies host ports `8123:8123` and `9000:9000`, matching `test-DWH`.

