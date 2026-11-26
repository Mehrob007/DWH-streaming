#!/usr/bin/env python3
"""
Simple helper to create bucket and upload raw data to RustFS S3.
Uses boto3 if installed, or guides the user.
"""
import sys
import os

try:
    import boto3
    from botocore.client import Config
    
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9002',
        aws_access_key_id='rustfsadmin',
        aws_secret_access_key='rustfsadmin123',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    
    bucket = 'bronze'
    try:
        s3.create_bucket(Bucket=bucket)
        print(f"Bucket '{bucket}' created.")
    except Exception as e:
        print(f"Bucket note: {e}")
        
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'orders_raw.csv')
    if os.path.exists(csv_path):
        s3.upload_file(csv_path, bucket, 'orders_raw.csv')
        print(f"Successfully uploaded {csv_path} to s3://{bucket}/orders_raw.csv")
    else:
        print(f"Warning: {csv_path} not found.")

except ImportError:
    print("boto3 not installed. You can upload via the RustFS Web Console at http://localhost:9001")

