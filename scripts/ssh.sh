#!/bin/bash
# Quick SSH access to EC2 instance

cd "$(dirname "$0")/../terraform"
EC2_IP=$(terraform output -raw instance_public_ip 2>/dev/null) || {
  echo "ERROR: Could not get EC2 IP. Run 'terraform apply' first."
  exit 1
}

echo "Connecting to $EC2_IP..."
ssh -i ~/.ssh/sentra-key.pem ec2-user@$EC2_IP
