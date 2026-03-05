"""Configuration for inventory management system."""
import os
import boto3
from botocore.config import Config

ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "inventory-data")
REGION = os.environ.get("AWS_REGION", "us-west-2")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2")

sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=REGION)
s3_client = boto3.client(
    "s3", region_name=REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"})
)
