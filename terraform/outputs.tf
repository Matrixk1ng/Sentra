output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_eip.sentra.public_ip
}

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.sentra.id
}

output "ecr_frontend_url" {
  description = "ECR Frontend Repository URL"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_backend_url" {
  description = "ECR Backend Repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "app_url" {
  description = "Application URL"
  value       = "http://${aws_eip.sentra.public_ip}"
}

output "api_url" {
  description = "API URL"
  value       = "http://${aws_eip.sentra.public_ip}:8000"
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_eip.sentra.public_ip}"
}
