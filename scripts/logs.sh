#!/bin/bash
# View logs from EC2 instance

SERVICE=${1:-""}

cd "$(dirname "$0")/../terraform"
EC2_IP=$(terraform output -raw instance_public_ip 2>/dev/null) || {
  echo "ERROR: Could not get EC2 IP. Run 'terraform apply' first."
  exit 1
}

if [ -z "$SERVICE" ]; then
  echo "Viewing all logs from $EC2_IP..."
  ssh -i ~/.ssh/sentra-key.pem ec2-user@$EC2_IP "cd sentra && docker-compose logs -f --tail=100"
else
  echo "Viewing $SERVICE logs from $EC2_IP..."
  ssh -i ~/.ssh/sentra-key.pem ec2-user@$EC2_IP "cd sentra && docker-compose logs -f --tail=100 $SERVICE"
fi
