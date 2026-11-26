# test-data-generator Specification

## Purpose
Generates realistic synthetic order transactions and loads them directly into S3 object storage for local testing and validation.

## Requirements

### Requirement: Synthetic Order Schema Generation
The generator SHALL produce order records containing order ID, customer ID, order timestamp, status, total monetary amount, and item details.

#### Scenario: Valid order record payload structure
- **WHEN** synthetic orders are generated
- **THEN** each record contains valid JSON or CSV fields adhering to the expected order schema

### Requirement: Automated S3 Data Seeding
The system SHALL automatically seed test order datasets into the configured S3 bucket during container startup or via an initialization command.

#### Scenario: Test data uploaded to S3
- **WHEN** the initialization or generator service completes execution
- **THEN** sample order data files are present in the designated S3 bucket and accessible for read operations
