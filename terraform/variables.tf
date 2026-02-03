variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro" # Free tier eligible
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH (your IP)"
  type        = string
  default     = "0.0.0.0/0" # Restrict to your IP in production
}

variable "youtube_api_key" {
  description = "YouTube API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bluesky_handle" {
  description = "Bluesky handle"
  type        = string
  default     = ""
}

variable "bluesky_app_password" {
  description = "Bluesky app password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "reddit_client_id" {
  description = "Reddit Client ID"
  type        = string
  default     = ""
}

variable "reddit_client_secret" {
  description = "Reddit Client Secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
  default     = "sentra_secure_password_123"
}
