# Spec Delta: Test Data Generator

## MODIFIED Requirements

### Requirement: Synthetic Order Schema Generation
The generator SHALL produce order records containing order ID, order date, client name, city, and amount, matching the test schema from the reference implementation.

#### Scenario: Valid order record payload structure
- **WHEN** synthetic orders are generated
- **THEN** each record contains order_id, order_date, client, city, and monetary amount fields

### Requirement: Automated S3 Data Seeding
The system SHALL continuously stream generated order events into the Kafka broker while also maintaining raw order datasets in the S3 `bronze` bucket.

#### Scenario: Test data uploaded to S3
- **WHEN** the generator runs in streaming mode
- **THEN** new order transactions are published to the Kafka topic and available in S3 storage
