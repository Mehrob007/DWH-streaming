#!/usr/bin/env python3
"""
Synthetic Order Data Generator for DWH Streaming S3 Lakehouse.
Generates realistic order events formatted as NDJSON (newline-delimited JSON).
"""

import argparse
import json
import os
import random
import uuid
from datetime import datetime, timedelta

STATUSES = ["completed", "pending", "shipped", "cancelled", "refunded"]
PRODUCTS = [
    ("Laptop Pro 15", 1299.99),
    ("Wireless Mouse", 29.50),
    ("Mechanical Keyboard", 89.90),
    ("USB-C Hub", 39.00),
    ("4K Monitor 27\"", 349.99),
    ("Ergonomic Chair", 249.00),
    ("Noise-Cancelling Headphones", 199.50),
    ("Webcam HD 1080p", 59.99),
    ("Desk Mat", 19.90),
    ("Smartphone Stand", 14.50),
]


def generate_single_order(base_date: datetime) -> dict:
    order_id = str(uuid.uuid4())
    user_id = random.randint(1001, 1999)

    random_seconds = random.randint(0, 86400 * 30)
    order_time = base_date - timedelta(seconds=random_seconds)

    num_items = random.randint(1, 4)
    chosen_products = random.sample(PRODUCTS, k=num_items)

    items = []
    total_amount = 0.0

    for idx, (prod_name, unit_price) in enumerate(chosen_products, start=1):
        quantity = random.randint(1, 3)
        item_total = round(unit_price * quantity, 2)
        total_amount += item_total
        items.append({
            "item_id": idx,
            "product_name": prod_name,
            "price": unit_price,
            "quantity": quantity,
            "item_total": item_total
        })

    total_amount = round(total_amount, 2)

    return {
        "order_id": order_id,
        "user_id": user_id,
        "order_date": order_time.strftime("%Y-%m-%d"),
        "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": random.choice(STATUSES),
        "currency": "USD",
        "total_amount": total_amount,
        "items_count": sum(i["quantity"] for i in items),
        "items": items
    }


def generate_orders_file(output_path: str, count: int = 1000):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    base_date = datetime.now()

    with open(output_path, "w", encoding="utf-8") as f:
        for _ in range(count):
            order = generate_single_order(base_date)
            f.write(json.dumps(order, ensure_ascii=False) + "\n")

    print(f"Generated {count} orders to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic orders dataset")
    parser.add_argument("--count", type=int, default=1000, help="Number of orders to generate")
    parser.add_argument("--output", type=str, default="data/orders_sample.json", help="Output file path (NDJSON)")
    args = parser.parse_args()

    generate_orders_file(args.output, args.count)


if __name__ == "__main__":
    main()

