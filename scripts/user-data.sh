#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user-data script at $(date)"

# Update system
yum update -y

# Add swap space (2GB) for t2.micro - prevents OOM when loading ML model
SWAP_SIZE_GB=2
echo "Configuring ${SWAP_SIZE_GB}GB swap..."
dd if=/dev/zero of=/swapfile bs=1M count=$((SWAP_SIZE_GB * 1024)) status=progress
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
echo "Swap configured. $(free -h | grep Swap)"

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
ENVEOF

# Create Caddyfile for HTTPS
cat > Caddyfile << 'CADDYEOF'
sentraai.duckdns.org {
    handle /health {
        reverse_proxy backend:8000
    }
    handle /search* {
        reverse_proxy backend:8000
    }
    handle /analyze* {
        reverse_proxy backend:8000
    }
    handle /history* {
        reverse_proxy backend:8000
    }
    handle {
        reverse_proxy frontend:3000
    }
}
CADDYEOF

# Create docker-compose.yml for production
cat > docker-compose.yml << 'COMPOSEEOF'
services:
  caddy:
    image: caddy:2-alpine
    container_name: sentra-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - frontend
      - backend

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
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${postgres_password}@db:5432/sentra
      - YOUTUBE_API_KEY=${youtube_api_key}
      - BLUESKY_HANDLE=${bluesky_handle}
      - BLUESKY_APP_PASSWORD=${bluesky_app_password}
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
    environment:
      - NEXT_PUBLIC_API_URL=https://sentraai.duckdns.org
    expose:
      - "3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  huggingface_cache:
  caddy_data:
  caddy_config:
COMPOSEEOF

# Set ownership
chown -R ec2-user:ec2-user /home/ec2-user/sentra

echo "User-data script completed at $(date)"
echo "Run deploy script to start application."