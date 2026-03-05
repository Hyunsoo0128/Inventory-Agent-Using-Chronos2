#!/bin/bash

BUCKET_NAME=${S3_BUCKET_NAME:-"inventory-data"}
REGION=${AWS_REGION:-"us-west-2"}

echo "Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

echo "Uploading sample data..."
aws s3 cp sample_data/product_1.csv s3://$BUCKET_NAME/sales/product_1.csv
aws s3 cp sample_data/product_2.csv s3://$BUCKET_NAME/sales/product_2.csv
aws s3 cp sample_data/current_stock.json s3://$BUCKET_NAME/inventory/current_stock.json
aws s3 cp sample_data/product_config.json s3://$BUCKET_NAME/config/product_config.json

echo "✅ Setup complete!"
echo ""
echo "S3 structure:"
aws s3 ls s3://$BUCKET_NAME/ --recursive
