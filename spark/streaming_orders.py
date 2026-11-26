#!/usr/bin/env python3
"""
PySpark Structured Streaming Pipeline: Kafka -> Spark -> ClickHouse.
Ingests continuous order events from Redpanda, cleans/validates them,
and writes micro-batches into ClickHouse sales.orders_clean.
"""

import sys
import clickhouse_connect
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DecimalType,
    LongType,
    StringType,
    StructField,
    StructType,
)

# 1. Initialize Spark Session with streaming configurations
spark = (
    SparkSession.builder
    .appName("streaming_orders_pipeline")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.ansi.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

print("=== Spark Structured Streaming Pipeline Starting ===", file=sys.stderr)

# 2. Define expected order JSON schema
order_schema = StructType([
    StructField("order_id", LongType(), True),
    StructField("order_date", StringType(), True),
    StructField("client", StringType(), True),
    StructField("city", StringType(), True),
    StructField("amount", DecimalType(12, 2), True),
])

# 3. Read stream from Kafka (Redpanda)
raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "redpanda:29092")
    .option("subscribe", "orders_stream")
    .option("startingOffsets", "earliest")
    .option("failOnDataLoss", "false")
    .load()
)

# 4. Parse JSON stream payload
parsed = (
    raw_stream
    .select(F.from_json(F.col("value").cast("string"), order_schema).alias("data"))
    .select("data.*")
)

# 5. Clean, normalize, and validate data
clean = (
    parsed
    .withColumn("order_id", F.col("order_id").cast("long"))
    .withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd"))
    .withColumn("client", F.trim("client"))
    .withColumn("city", F.initcap(F.trim("city")))
    .withColumn("amount", F.col("amount").cast("decimal(12,2)"))
)

# Quality filter: reject records missing order_id, order_date, or amount
valid_orders = clean.filter(
    F.col("order_id").isNotNull()
    & F.col("order_date").isNotNull()
    & F.col("amount").isNotNull()
)


# 6. Micro-batch sink function into ClickHouse
def write_to_clickhouse(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    # Deduplicate within micro-batch
    batch_dedup = batch_df.dropDuplicates(["order_id"])
    records = batch_dedup.collect()
    if not records:
        return

    rows = [[r.order_id, r.order_date, r.client, r.city, r.amount] for r in records]

    try:
        ch_client = clickhouse_connect.get_client(
            host="clickhouse", port=8123, username="admin", password="admin123"
        )
        ch_client.insert(
            "sales.orders_clean",
            rows,
            column_names=["order_id", "order_date", "client", "city", "amount"]
        )
        print(f"[Batch {batch_id}] Ingested {len(rows)} orders into sales.orders_clean", flush=True)
    except Exception as ex:
        print(f"[Batch {batch_id}] Error inserting into ClickHouse: {ex}", file=sys.stderr, flush=True)


# 7. Start streaming query
query = (
    valid_orders.writeStream
    .trigger(processingTime="2 seconds")
    .foreachBatch(write_to_clickhouse)
    .option("checkpointLocation", "/tmp/spark-checkpoints/orders")
    .start()
)

print("Streaming query active. Awaiting new orders...", file=sys.stderr)
query.awaitTermination()

