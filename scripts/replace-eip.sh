#!/bin/bash
# Replace Elastic IP - fixes "can't reach" when AWS assigns an IP in 100.x range
# (many networks don't route that range)

set -e
cd "$(dirname "$0")/../terraform"

echo "=== Replacing Elastic IP ==="
echo "This will release 100.49.83.59 and assign a new public IP."
echo ""

# Remove EIP association first, then EIP
terraform destroy -target=aws_eip_association.sentra -target=aws_eip.sentra -auto-approve

echo ""
echo "Creating new Elastic IP..."
terraform apply -target=aws_eip.sentra -target=aws_eip_association.sentra -auto-approve

NEW_IP=$(terraform output -raw instance_public_ip)
echo ""
echo "=== Done! ==="
echo "New public IP: $NEW_IP"
echo ""
echo "Try:  http://$NEW_IP"
echo "SSH:  ./scripts/ssh.sh"
echo ""
