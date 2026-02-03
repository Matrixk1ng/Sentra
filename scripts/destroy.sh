#!/bin/bash
set -e

echo "=== DESTROYING Sentra Infrastructure ==="
echo ""
echo "WARNING: This will delete ALL AWS resources including:"
echo "  - EC2 instance"
echo "  - ECR repositories (and all images)"
echo "  - Security groups"
echo "  - Elastic IP"
echo "  - IAM roles"
echo ""
echo "The S3 state bucket will be preserved."
echo ""
read -p "Type 'destroy' to confirm: " confirm

if [ "$confirm" != "destroy" ]; then
  echo "Aborted."
  exit 1
fi

cd "$(dirname "$0")/../terraform"

echo ""
echo "Running terraform destroy..."
terraform destroy -auto-approve

echo ""
echo "=========================================="
echo "  Infrastructure Destroyed"
echo "=========================================="
echo ""
echo "Note: S3 state bucket preserved. Delete manually if needed:"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "UNKNOWN")
echo "  aws s3 rb s3://sentra-tfstate-$AWS_ACCOUNT_ID --force"
echo ""
