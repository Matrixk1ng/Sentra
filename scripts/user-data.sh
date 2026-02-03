#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user-data script at $(date)"

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install -y git

# Create app directory
mkdir -p /home/ec2-user/sentra
cd /home/ec2-user/sentra

# Create .env file
cat > .env << 'ENVEOF'
DATABASE_URL=postgresql://postgres:${postgres_password}@db:5432/sentra
POSTGRES_PASSWORD=${postgres_password}
YOUTUBE_API_KEY=${youtube_api_key}
BLUESKY_HANDLE=${bluesky_handle}
BLUESKY_APP_PASSWORD=${bluesky_app_password}
REDDIT_CLIENT_ID=${reddit_client_id}
REDDIT_CLIENT_SECRET=${reddit_client_secret}
REDDIT_USER_AGENT=sentra:v1.0.0
ENVEOF

# Create docker-compose.yml for production
cat > docker-compose.yml << 'COMPOSEEOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: sentra-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${postgres_password}
      POSTGRES_DB: sentra
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    image: ${account_id}.dkr.ecr.${aws_region}.amazonaws.com/sentra-backend:latest
    container_name: sentra-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${postgres_password}@db:5432/sentra
      - YOUTUBE_API_KEY=${youtube_api_key}
      - BLUESKY_HANDLE=${bluesky_handle}
      - BLUESKY_APP_PASSWORD=${bluesky_app_password}
      - REDDIT_CLIENT_ID=${reddit_client_id}
      - REDDIT_CLIENT_SECRET=${reddit_client_secret}
      - REDDIT_USER_AGENT=sentra:v1.0.0
      - HF_HOME=/root/.cache/huggingface
      - TRANSFORMERS_CACHE=/root/.cache/huggingface
    volumes:
      - huggingface_cache:/root/.cache/huggingface
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s

  frontend:
    image: ${account_id}.dkr.ecr.${aws_region}.amazonaws.com/sentra-frontend:latest
    container_name: sentra-frontend
    restart: unless-stopped
    ports:
      - "80:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  huggingface_cache:
COMPOSEEOF

# Set ownership
chown -R ec2-user:ec2-user /home/ec2-user/sentra

echo "User-data script completed at $(date)"
echo "Run deploy script to start application."
