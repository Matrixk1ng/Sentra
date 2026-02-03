# Sentra Deployment Guide (AWS Free Tier)

This guide walks you through deploying Sentra to AWS, optimized for the free tier ($0/month).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS Cloud (Free Tier)                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     EC2 (t2.micro)                          │ │
│  │                     - Docker Compose                         │ │
│  │                     - Frontend + Backend + DB                │ │
│  │                     - 750 hrs/month FREE                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐       │
│  │     ECR      │    │   Elastic    │    │     S3       │       │
│  │  (Images)    │    │      IP      │    │ (TF State)   │       │
│  │  500MB FREE  │    │   (Free if   │    │  5GB FREE    │       │
│  └──────────────┘    │   attached)  │    └──────────────┘       │
│                      └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## Cost Breakdown

| Resource | Free Tier Limit | Our Usage | Monthly Cost |
|----------|-----------------|-----------|--------------|
| EC2 t2.micro | 750 hrs/month | 720 hrs | $0 |
| EBS (20GB) | 30 GB | 20 GB | $0 |
| ECR | 500 MB | ~200 MB | $0 |
| S3 | 5 GB | <1 MB | $0 |
| Elastic IP | Free if attached | 1 attached | $0 |
| Data Transfer | 100 GB out | ~5 GB | $0 |
| **Total** | | | **$0/mo** |

> Note: Free tier lasts 12 months from AWS account creation.

---

## Prerequisites

Before starting, ensure you have:

- **AWS Account** (free tier eligible)
- **AWS CLI** installed and configured
- **Terraform** installed (v1.0+)
- **Docker** installed
- **Git** installed

### Install Prerequisites

```bash
# AWS CLI (macOS)
brew install awscli

# AWS CLI (Windows) - Download from https://aws.amazon.com/cli/

# Terraform (macOS)
brew install terraform

# Terraform (Windows) - Download from https://terraform.io/downloads
```

---

## Step 1: Configure AWS CLI

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Your IAM user access key
- **AWS Secret Access Key**: Your IAM user secret key
- **Default region**: `us-east-1`
- **Default output format**: `json`

### Required IAM Permissions

Your IAM user needs these permissions:
- `AmazonEC2FullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonS3FullAccess`
- `IAMFullAccess` (or limited IAM permissions)

---

## Step 2: Run Setup Script

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup-infrastructure.sh
```

This script will:
1. Verify AWS credentials
2. Create SSH key pair (`sentra-key`)
3. Create S3 bucket for Terraform state
4. Initialize Terraform
5. Create `terraform.tfvars` template

---

## Step 3: Configure Variables

Edit `terraform/terraform.tfvars` with your API keys:

```hcl
aws_region       = "us-east-1"
instance_type    = "t2.micro"
key_name         = "sentra-key"
allowed_ssh_cidr = "YOUR.IP.ADDRESS/32"  # Your IP for SSH access

# API Keys
youtube_api_key      = "your_youtube_api_key"
bluesky_handle       = "yourhandle.bsky.social"
bluesky_app_password = "your_app_password"
reddit_client_id     = "your_reddit_client_id"
reddit_client_secret = "your_reddit_client_secret"

# Database
postgres_password = "choose_a_secure_password"
```

---

## Step 4: Deploy Infrastructure

```bash
cd terraform

# Preview changes
terraform plan

# Apply changes
terraform apply
```

Type `yes` when prompted. This creates:
- EC2 instance (t2.micro)
- ECR repositories (frontend + backend)
- Security groups
- Elastic IP
- IAM roles

---

## Step 5: Deploy Application

```bash
./scripts/deploy.sh
```

This script will:
1. Build Docker images locally
2. Push images to ECR
3. SSH into EC2 and pull images
4. Start containers with Docker Compose

---

## Step 6: Access Application

Get the URL:
```bash
cd terraform
terraform output app_url
```

- **Frontend**: `http://<EC2_IP>`
- **Backend API**: `http://<EC2_IP>:8000`
- **Health Check**: `http://<EC2_IP>:8000/health`

---

## GitHub Actions Setup (CI/CD)

### Add Repository Secrets

Go to: GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM user secret key |
| `EC2_HOST` | EC2 public IP (from `terraform output instance_public_ip`) |
| `SSH_PRIVATE_KEY` | Contents of `~/.ssh/sentra-key.pem` |

### Get SSH Key Contents

```bash
cat ~/.ssh/sentra-key.pem
```

Copy the entire output including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`.

### Workflow Triggers

- **CI** (`ci.yml`): Runs on every push and PR
  - Lints frontend and backend
  - Builds Docker images
  - Validates Terraform

- **Deploy** (`deploy.yml`): Runs on push to `main`
  - Builds and pushes images to ECR
  - SSHs to EC2 and deploys
  - Runs health check

---

## Useful Commands

### SSH to EC2
```bash
./scripts/ssh.sh
# or
ssh -i ~/.ssh/sentra-key.pem ec2-user@<EC2_IP>
```

### View Logs
```bash
./scripts/logs.sh           # All services
./scripts/logs.sh backend   # Backend only
./scripts/logs.sh frontend  # Frontend only
```

### Manual Deployment
```bash
./scripts/deploy.sh
```

### Restart Services
```bash
ssh -i ~/.ssh/sentra-key.pem ec2-user@<EC2_IP> "cd sentra && docker-compose restart"
```

### View Service Status
```bash
ssh -i ~/.ssh/sentra-key.pem ec2-user@<EC2_IP> "cd sentra && docker-compose ps"
```

---

## Destroying Infrastructure

To tear down all AWS resources:

```bash
./scripts/destroy.sh
```

> Note: S3 state bucket is preserved. Delete manually if needed.

---

## Troubleshooting

### "Sentiment model not loaded"

The ML model downloads on first start (~500MB). Wait 2-3 minutes and check logs:
```bash
./scripts/logs.sh backend
```

### "Connection refused" on port 8000

Backend might still be starting. Wait for health check to pass:
```bash
curl http://<EC2_IP>:8000/health
```

### "Out of memory"

t2.micro has 1GB RAM. The ML model uses most of it. If you see OOM errors:
1. Reduce model size, or
2. Upgrade to t3.small (~$15/month)

### ECR login issues

Manually login to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com
```

### SSH permission denied

Check key permissions:
```bash
chmod 400 ~/.ssh/sentra-key.pem
```

---

## Security Recommendations

For production use:

1. **Restrict SSH access**: Set `allowed_ssh_cidr` to your IP only
2. **Use HTTPS**: Add SSL certificate with Let's Encrypt
3. **Rotate credentials**: Regularly rotate API keys and passwords
4. **Enable CloudWatch**: Monitor EC2 metrics
5. **Set up backups**: Backup PostgreSQL data volume

---

## Resume Bullet Points

After deploying, you can add these to your resume:

- Deployed full-stack sentiment analysis platform to AWS using Terraform IaC
- Implemented CI/CD pipeline with GitHub Actions for automated testing and deployment
- Containerized Python ML backend (HuggingFace Transformers) and Next.js frontend with Docker
- Configured AWS ECR for container registry, EC2 for compute, with security groups
- Optimized cloud architecture for cost efficiency ($0/month on AWS Free Tier)
