# Deploy Runbook (Preview)
1) Build & push images → ECR
2) Create/Update ECS task defs (api/worker)
3) Create services (api behind ALB, worker scheduled)
4) Set Secrets Manager values and task envs
5) Smoke test /health and worker logs
6) Rollback: switch to previous image tag
