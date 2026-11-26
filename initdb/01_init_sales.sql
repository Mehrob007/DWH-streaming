-- =============================================================================
-- ClickHouse DWH Sales Schema Initialization
-- Matching test-DWH schema with streaming ingestion support
-- =============================================================================

CREATE DATABASE IF NOT EXISTS sales;

CREATE TABLE IF NOT EXISTS sales.orders_clean
(
    order_id    UInt64,
    order_date  Date,
    client      String,
    city        String,
    amount      Decimal(12, 2),
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, order_id);

-- Aggregated analytics view for Superset dashboards
CREATE VIEW IF NOT EXISTS sales.v_city_summary AS
SELECT
    city,
    count() AS total_orders,
    uniqExact(client) AS unique_clients,
    round(sum(amount), 2) AS total_revenue,
    round(avg(amount), 2) AS avg_order_value
FROM sales.orders_clean
GROUP BY city
ORDER BY total_revenue DESC;

