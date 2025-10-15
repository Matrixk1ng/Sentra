# Infra Notes
Local: Docker Compose (db, redis, api, worker, frontend)  
Prod: AWS ECS Fargate (api public via ALB, worker scheduled), RDS Postgres, ElastiCache Redis (or self-managed later), S3 (raw, artifacts), ACM cert on ALB.  
Secrets: AWS Secrets Manager (document keys: reddit creds, db url, redis url).
