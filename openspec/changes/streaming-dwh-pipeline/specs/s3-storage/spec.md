# Spec Delta: S3 Storage

## MODIFIED Requirements

### Requirement: S3 Object Storage Service
The system SHALL provide an S3-compatible object storage service running RustFS via Docker Compose, exposing the S3 API on port 9002 and the Web Console on port 9001.

#### Scenario: Service health and readiness
- **WHEN** the RustFS storage service is started via `docker compose up`
- **THEN** the S3 API endpoint is healthy and responds to S3 requests on port 9002, and the web console is accessible on port 9001

### Requirement: Default Bucket Provisioning
The system SHALL automatically create default buckets including `bronze` for raw data landing upon startup if they do not already exist.

#### Scenario: Auto-creation of orders bucket
- **WHEN** the storage service and initialization routines complete startup
- **THEN** the target bucket `bronze` exists and is ready to accept read and write operations
