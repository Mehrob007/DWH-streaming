# dwh-core Specification

## Purpose
Provides a containerized analytical database engine capable of storing schemas and querying order datasets directly from S3 object storage.

## Requirements

### Requirement: Analytical Engine Service
The system SHALL provide a containerized columnar analytical database service that starts reliably via Docker Compose.

#### Scenario: Database engine startup
- **WHEN** the DWH core service is started via `docker compose up`
- **THEN** the database service accepts client connections on its configured query and HTTP ports

### Requirement: S3 Table Integration and Querying
The DWH engine SHALL support querying order data directly from the S3 storage bucket using S3 table functions or external table definitions.

#### Scenario: Querying S3 orders data
- **WHEN** an analytical query is executed targeting the S3 orders dataset
- **THEN** the DWH engine reads objects from S3 and returns aggregated or filtered order records

### Requirement: Orders Table Schema Initialization
The system SHALL automatically initialize the analytical orders schema and table definitions upon first startup.

#### Scenario: Automatic schema migration on startup
- **WHEN** the database container starts up for the first time
- **THEN** the target database and analytical orders table are created and ready for queries
