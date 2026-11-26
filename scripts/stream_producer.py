#!/usr/bin/env python3
"""
Streaming Order Event Generator for Kafka (Redpanda) & S3 (RustFS).
Generates realistic order streams matching test-DWH schema:
(order_id, order_date, client, city, amount)
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta

CLIENTS = ["Kolya", " Aziz ", "Sitora", "Rustam", "Kurbonali", "Dilshod", " Madina ", "Farrukh"]
CITIES = ["Dushanbe", "dushanbe", "Khujand", "Bokhtar", "Kulob", "Istaravshan", "Panjakent"]


def generate_single_order(order_id: int) -> dict:
    today = datetime.now()
    order_date = (today - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d")

    client = random.choice(CLIENTS)
    city = random.choice(CITIES)

    # 10% chance of missing amount to simulate real dirty stream data
    if random.random() < 0.10:
        amount = None
    else:
        amount = round(random.uniform(50.0, 3500.0), 2)

    return {
        "order_id": order_id,
        "order_date": order_date,
        "client": client,
        "city": city,
        "amount": amount
    }


def stream_orders(interval_sec: float = 1.0, max_count: int = 0):
    order_id = 1000
    count = 0
    print(f"Starting order stream (interval: {interval_sec}s)...", file=sys.stderr)

    try:
        while True:
            order_id += 1
            order = generate_single_order(order_id)
            # Output line of JSON
            try:
                print(json.dumps(order, ensure_ascii=False), flush=True)
            except BrokenPipeError:
                # Pipe closed by consumer
                break

            count += 1
            if max_count > 0 and count >= max_count:
                break

            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print(f"\nStopped after {count} orders.", file=sys.stderr)


def generate_batch_csv(output_path: str, count: int = 100):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("order_id,order_date,client,city,amount\n")
        for i in range(1, count + 1):
            order = generate_single_order(100 + i)
            amt_str = str(order["amount"]) if order["amount"] is not None else ""
            f.write(f"{order['order_id']},{order['order_date']},{order['client']},{order['city']},{amt_str}\n")
    print(f"Generated {count} raw orders to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Streaming Order Producer")
    parser.add_argument("--stream", action="store_true", help="Run continuous streaming mode to stdout")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between streaming events")
    parser.add_argument("--count", type=int, default=10, help="Number of events (0 for infinite)")
    parser.add_argument("--csv", type=str, default="", help="Export static raw CSV file path")
    args = parser.parse_args()

    if args.csv:
        generate_batch_csv(args.csv, args.count if args.count > 0 else 100)
    else:
        stream_orders(args.interval, args.count)


if __name__ == "__main__":
    main()

