#!/bin/bash
set -e

echo "=== Deploying Sentra ==="
echo ""

# Get AWS info
AWS_REGION=$(aws configure get region || echo "us-east-1")
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "ECR URL: $ECR_URL"

# Get EC2 IP from Terraform
cd "$(dirname "$0")/../terraform"
EC2_IP=$(terraform output -raw instance_public_ip 2>/dev/null) || {
  echo "ERROR: Could not get EC2 IP. Run 'terraform apply' first."
  exit 1
}
cd - > /dev/null

echo "EC2 IP: $EC2_IP"
echo ""

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
echo "✓ ECR login successful"

# Build and push frontend
echo ""
echo "Building frontend..."
docker build -t sentra-frontend:latest ./frontend
docker tag sentra-frontend:latest $ECR_URL/sentra-frontend:latest
echo "Pushing frontend to ECR..."
docker push $ECR_URL/sentra-frontend:latest
echo "✓ Frontend pushed"

# Build and push backend
echo ""
echo "Building backend..."
docker build -t sentra-backend:latest ./backend
docker tag sentra-backend:latest $ECR_URL/sentra-backend:latest
echo "Pushing backend to ECR..."
docker push $ECR_URL/sentra-backend:latest
echo "✓ Backend pushed"

# Deploy on EC2
echo ""
echo "Deploying on EC2..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i ~/.ssh/sentra-key.pem ec2-user@$EC2_IP << ENDSSH
set -e
cd /home/ec2-user/sentra

echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL

echo "Pulling latest images..."
docker-compose pull

echo "Restarting services..."
docker-compose down || true
docker-compose up -d

echo "Cleaning up old images..."
docker system prune -f

echo "Service status:"
docker-compose ps
ENDSSH

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Application URL: http://$EC2_IP"
echo "Backend API:     http://$EC2_IP:8000"
echo "Health Check:    http://$EC2_IP:8000/health"
echo ""
echo "View logs: ssh -i ~/.ssh/sentra-key.pem ec2-user@$EC2_IP 'cd sentra && docker-compose logs -f'"
echo ""
