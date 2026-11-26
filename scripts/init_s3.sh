#!/bin/sh
set -e

echo "=== MinIO Initialization ==="
echo "Target S3 endpoint: http://minio:9000"
echo "Target bucket: ${S3_BUCKET_NAME:-warehouse-raw}"

echo "Waiting for MinIO service..."
until /usr/bin/mc alias set local "http://minio:9000" "${MINIO_ROOT_USER:-minioadmin}" "${MINIO_ROOT_PASSWORD:-minioadmin}"; do
  echo "MinIO not ready yet, retrying in 2 seconds..."
  sleep 2
done

BUCKET="${S3_BUCKET_NAME:-warehouse-raw}"

echo "Creating bucket 'local/$BUCKET'..."
/usr/bin/mc mb --ignore-existing "local/$BUCKET"

echo "Configuring download policy for 'local/$BUCKET'..."
/usr/bin/mc anonymous set download "local/$BUCKET" || true

if [ -f /data-seed/orders_sample.json ]; then
  echo "Uploading sample orders data to local/$BUCKET/orders/orders_sample.json..."
  /usr/bin/mc cp /data-seed/orders_sample.json "local/$BUCKET/orders/orders_sample.json"
else
  echo "Notice: /data-seed/orders_sample.json not found."
fi

echo "=== MinIO Initialization Complete ==="
/usr/bin/mc ls "local/$BUCKET/orders/" || true
exit 0

