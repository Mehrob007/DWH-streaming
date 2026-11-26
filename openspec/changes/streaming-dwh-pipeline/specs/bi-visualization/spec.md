# Spec Delta: BI Visualization

## Purpose

Provides Apache Superset web analytics dashboard connected to ClickHouse for exploring real-time and historical orders data.

## ADDED Requirements

### Requirement: Superset Service Deployment
The system SHALL deploy an Apache Superset service with pre-installed ClickHouse connectivity accessible via a web browser on port 8088.

#### Scenario: Web UI login and accessibility
- **WHEN** an operator opens port 8088 in a web browser
- **THEN** the Superset login interface appears and accepts pre-configured administrator credentials

### Requirement: ClickHouse Data Source Integration
The system SHALL support connecting Superset directly to the ClickHouse `sales` database to query orders data.

#### Scenario: Running queries in SQL Lab
- **WHEN** a user queries ClickHouse tables in Superset SQL Lab
- **THEN** query results from `sales.orders_clean` are displayed interactively

