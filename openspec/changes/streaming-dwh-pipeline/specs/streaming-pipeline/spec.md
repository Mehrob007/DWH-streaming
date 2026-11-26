# Spec Delta: Streaming Pipeline

## Purpose

Provides continuous real-time stream ingestion, stream processing, schema validation, and micro-batch writes from Kafka to ClickHouse using Spark Structured Streaming.

## ADDED Requirements

### Requirement: Kafka Event Broker Service
The system SHALL provide a Kafka-compatible streaming broker service accepting order events on a dedicated topic.

#### Scenario: Broker readiness and topic creation
- **WHEN** the streaming broker starts up via `docker compose up`
- **THEN** client applications can publish and consume messages on the `orders_stream` topic

### Requirement: Continuous Stream Processing with Spark
The system SHALL run an Apache Spark Structured Streaming service that reads incoming events continuously from Kafka and applies cleaning and deduplication.

#### Scenario: Real-time stream transformation
- **WHEN** raw order events arrive in the Kafka topic
- **THEN** Spark parses the JSON/CSV records, normalizes string casing, validates mandatory fields, and produces structured rows

### Requirement: Micro-batch Ingestion into ClickHouse
The Spark streaming service SHALL write valid processed order records into ClickHouse tables in real time using micro-batches and state checkpoints.

#### Scenario: Delivery of cleaned records into ClickHouse
- **WHEN** a micro-batch of valid order events is processed by Spark
- **THEN** the records are persisted in ClickHouse table `sales.orders_clean` within seconds of arrival

