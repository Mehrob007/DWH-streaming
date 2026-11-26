#!/usr/bin/env bash
set -e

# ==============================================================================
# Verification script for DWH + S3 Docker Compose stack
# ==============================================================================

CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_HTTP_PORT:-8123}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-clickhouse}"
MINIO_HOST="${MINIO_HOST:-localhost}"
MINIO_PORT="${MINIO_API_PORT:-9000}"

echo "===================================================="
echo "DWH + S3 Environment Verification"
echo "===================================================="

# 1. Check MinIO health
echo -n "[1/4] Checking MinIO S3 API health... "
if curl -s -f "http://${MINIO_HOST}:${MINIO_PORT}/minio/health/live" > /dev/null; then
    echo "OK (Healthy)"
else
    echo "FAILED"
    echo "Error: MinIO S3 endpoint http://${MINIO_HOST}:${MINIO_PORT}/minio/health/live is not responding."
    exit 1
fi

# 2. Check ClickHouse health
echo -n "[2/4] Checking ClickHouse server ping... "
PING_RESP=$(curl -s "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/ping" || true)
if [ "$PING_RESP" = "Ok." ]; then
    echo "OK ($PING_RESP)"
else
    echo "FAILED"
    echo "Error: ClickHouse ping failed at http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/ping."
    exit 1
fi

# 3. Query count of orders in S3 table
echo "[3/4] Running query: count(*) from dwh.orders_s3..."
ORDERS_COUNT=$(curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT count() FROM dwh.orders_s3")

echo "Total orders detected in S3: ${ORDERS_COUNT}"

if [ -z "$ORDERS_COUNT" ] || [ "$ORDERS_COUNT" -eq 0 ]; then
    echo "Warning: No orders found in S3 table. Check if minio-init finished seeding data."
    exit 1
fi

# 4. Run sample analytical aggregation
echo "[4/4] Running analytical aggregation query (orders by status):"
echo "----------------------------------------------------"
curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT status, count() AS orders_cnt, round(sum(total_amount), 2) AS revenue FROM dwh.orders_s3 GROUP BY status ORDER BY orders_cnt DESC FORMAT PrettyCompact"

echo "----------------------------------------------------"
echo "Top daily sales preview (dwh.v_daily_sales):"
curl -s -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data-binary "SELECT * FROM dwh.v_daily_sales LIMIT 5 FORMAT PrettyCompact"

echo ""
echo "All verification checks passed successfully!"

