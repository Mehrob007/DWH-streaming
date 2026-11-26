#!/usr/bin/env bash
set -e

# ==============================================================================
# Verification script for Streaming DWH Pipeline
# Tests Redpanda (Kafka) -> Spark Structured Streaming -> ClickHouse -> Superset
# ==============================================================================

CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_HTTP_PORT:-8123}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-admin}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-admin123}"
RUSTFS_PORT="${RUSTFS_PORT:-9002}"

echo "===================================================="
echo "Streaming DWH Pipeline Verification"
echo "===================================================="

# 1. Check ClickHouse health
echo -n "[1/5] Checking ClickHouse server... "
PING_RESP=$(curl -s "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/ping" || true)
if [ "$PING_RESP" = "Ok." ]; then
    echo "OK ($PING_RESP)"
else
    echo "FAILED (ClickHouse ping failed at http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/ping)"
    exit 1
fi

# 2. Check RustFS S3 storage
echo -n "[2/5] Checking RustFS S3 endpoint (port ${RUSTFS_PORT})... "
if curl -s "http://localhost:${RUSTFS_PORT}/" > /dev/null 2>&1 || [ $? -eq 52 ]; then
    echo "OK (Responding)"
else
    echo "FAILED"
    echo "Notice: Ensure rustfs container is running via 'docker compose up -d rustfs'"
fi

# 3. Check Redpanda Kafka Broker
echo "[3/5] Verifying Redpanda broker & topic 'orders_stream'..."
REDPANDA_CONTAINER="dwh-redpanda"
docker exec "$REDPANDA_CONTAINER" rpk cluster info || docker exec redpanda rpk cluster info || true
docker exec "$REDPANDA_CONTAINER" rpk topic create orders_stream 2>/dev/null || docker exec redpanda rpk topic create orders_stream 2>/dev/null || true

# 4. Stream 10 new test orders into Kafka
echo "[4/5] Producing 10 synthetic order events into Kafka topic 'orders_stream'..."
python3 scripts/stream_producer.py --count 10 | (docker exec -i "$REDPANDA_CONTAINER" rpk topic produce orders_stream 2>/dev/null || docker exec -i redpanda rpk topic produce orders_stream)

echo "Awaiting Spark Structured Streaming micro-batch processing (5 seconds)..."
sleep 5

# 5. Verify records in ClickHouse sales.orders_clean
echo "[5/5] Checking ClickHouse sales.orders_clean table:"
echo "----------------------------------------------------"
ORDERS_COUNT=$(curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT count() FROM sales.orders_clean")

echo "Total cleaned orders in ClickHouse: ${ORDERS_COUNT}"

echo ""
echo "Recent streaming records in ClickHouse (sales.orders_clean):"
curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT order_id, order_date, client, city, amount, ingested_at FROM sales.orders_clean ORDER BY ingested_at DESC LIMIT 5 FORMAT PrettyCompact"

echo ""
echo "City summary view (sales.v_city_summary):"
curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT * FROM sales.v_city_summary LIMIT 5 FORMAT PrettyCompact"

echo ""
echo "===================================================="
echo "Verification complete!"
echo "Superset BI is accessible at: http://localhost:8088"
echo "RustFS S3 Console: http://localhost:9001"
echo "===================================================="

