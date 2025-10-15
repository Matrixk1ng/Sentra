# Architecture (MVP)
Worker: PRAW → (optional raw S3) → normalize → Postgres → NLP → aggregates  
API: FastAPI serves precomputed metrics & examples  
Frontend: Next.js renders leaderboards, entity detail, search  
Data: Postgres (primary), Redis (cache), S3 for raw/artifacts (optional in MVP)  
Runtime: Docker Compose (local), ECS Fargate (prod)  
Observability: Sentry (API/worker), CloudWatch (prod)

System map:
[Ingestion] → [Normalized PG] → [NLP signals] → [Aggregations] → [API] → [UI]
