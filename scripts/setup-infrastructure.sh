#!/bin/bash
set -e

echo "=== Sentra Infrastructure Setup (Free Tier) ==="
echo ""

# Check prerequisites
command -v aws >/dev/null 2>&1 || { echo "ERROR: AWS CLI required. Install from https://aws.amazon.com/cli/"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "ERROR: Terraform required. Install from https://terraform.io"; exit 1; }

# Check AWS credentials
echo "Checking AWS credentials..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null) || {
  echo "ERROR: AWS credentials not configured. Run 'aws configure' first."
  exit 1
}
echo "✓ AWS Account ID: $AWS_ACCOUNT_ID"

AWS_REGION=$(aws configure get region || echo "us-east-1")
echo "✓ AWS Region: $AWS_REGION"

# Create SSH key pair if it doesn't exist
KEY_NAME="sentra-key"
echo ""
echo "Checking SSH key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $AWS_REGION >/dev/null 2>&1; then
  echo "Creating SSH key pair..."
  mkdir -p ~/.ssh
  aws ec2 create-key-pair --key-name $KEY_NAME --region $AWS_REGION --query 'KeyMaterial' --output text > ~/.ssh/$KEY_NAME.pem
  chmod 400 ~/.ssh/$KEY_NAME.pem
  echo "✓ SSH key saved to ~/.ssh/$KEY_NAME.pem"
else
  echo "✓ SSH key pair '$KEY_NAME' already exists"
fi

# Create S3 bucket for Terraform state
BUCKET_NAME="sentra-tfstate-${AWS_ACCOUNT_ID}"
echo ""
echo "Setting up Terraform state bucket..."
if aws s3 ls "s3://$BUCKET_NAME" --region $AWS_REGION 2>/dev/null; then
  echo "✓ Bucket '$BUCKET_NAME' already exists"
else
  echo "Creating bucket: $BUCKET_NAME"
  if [ "$AWS_REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket $BUCKET_NAME --region $AWS_REGION
  else
    aws s3api create-bucket --bucket $BUCKET_NAME --region $AWS_REGION --create-bucket-configuration LocationConstraint=$AWS_REGION
  fi
  aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
  echo "✓ Bucket created with versioning enabled"
fi

# Update main.tf with account ID
echo ""
echo "Configuring Terraform..."
cd "$(dirname "$0")/../terraform"

# Replace ACCOUNT_ID placeholder
if grep -q "ACCOUNT_ID" main.tf; then
  sed -i.bak "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" main.tf
  rm -f main.tf.bak
  echo "✓ Updated main.tf with account ID"
fi

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
  echo ""
  echo "Creating terraform.tfvars..."
  cp terraform.tfvars.example terraform.tfvars
  sed -i.bak "s/key_name.*=.*/key_name = \"$KEY_NAME\"/g" terraform.tfvars
  rm -f terraform.tfvars.bak
  echo "✓ Created terraform.tfvars - PLEASE EDIT WITH YOUR API KEYS"
fi

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
terraform init

# Validate configuration
echo ""
echo "Validating Terraform configuration..."
terraform validate
echo "✓ Configuration valid"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit terraform/terraform.tfvars with your API keys"
echo "2. Run: cd terraform && terraform plan"
echo "3. Run: cd terraform && terraform apply"
echo "4. Run: ./scripts/deploy.sh"
echo ""
echo "Estimated monthly cost: \$0 (within AWS Free Tier)"
echo ""
