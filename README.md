# Sentra
🚀 Overview
Social Media Sentiment is an analytics platform designed to measure and visualize sentiment trends from platforms such as X (Twitter), Reddit, and YouTube.
It leverages AI-driven natural language processing (NLP) to classify public opinion on trending topics, brands, and events — in real time.

The goal is to help users, researchers, and organizations understand how the internet feels about anything — instantly.

🧩 Features

🔍 Multi-platform Sentiment Analysis – Aggregate posts from Twitter/X, Reddit, and YouTube comments.

💬 AI-Based Classification – Uses transformer models to classify sentiments as Positive, Negative, or Neutral.

📊 Data Visualization Dashboard – Interactive graphs to display sentiment distribution and trend shifts.

⚙️ Custom Topic Tracking – Input any hashtag, keyword, or phrase and view live sentiment results.

💾 Historical Data Comparison – Track how sentiment evolves over time.

🌐 API Integration Ready – Modular backend design for easy integration into other tools or dashboards.

🏗️ Tech Stack
Layer	Technology
Frontend	React / Next.js with Tailwind CSS
Backend	FastAPI (Python) or Node.js Express
Database	PostgreSQL (via Prisma ORM)
AI/NLP	HuggingFace Transformers (BERT / RoBERTa sentiment models)
Containerization	Docker & Docker Compose
Deployment	Render / AWS EC2 / Railway (configurable)
🧰 Setup & Installation
# 1. Clone the repository
git clone https://github.com/<your-username>/social-media-sentiment.git

# 2. Navigate to the project folder
cd social-media-sentiment

# 3. Start Docker containers (for DB + API)
docker-compose up -d

# 4. Install dependencies (frontend/backend)
npm install
# or
pip install -r requirements.txt

# 5. Run the app locally
npm run dev
# or
uvicorn main:app --reload


The app should now be live on
👉 http://localhost:3000 for frontend
👉 http://localhost:8000 for backend API

📈 Example Workflow

Enter a keyword or hashtag (e.g. “#AI”, “Tesla”, “Elections 2025”).

The system fetches recent posts from connected APIs.

AI models analyze text and classify sentiment.

The frontend displays a sentiment pie chart + trendline over time.

🧪 Development Notes

Designed for extensibility — easily add new platforms or ML models.

Dockerized for consistent local and production environments.

Future iterations will include:

🧵 Threaded discussion analysis (contextual sentiment)

🗺️ Geo-based sentiment mapping

🧬 Custom fine-tuning pipeline for domain-specific topics


sentra/
├─ README.md
├─ .gitignore
├─ .env.example                  # copy → .env for local dev (never commit real secrets)
├─ docker-compose.yml            # local: runs API + worker + Postgres + Redis
├─ infra/
│  ├─ aws/
│  │  ├─ ecs-task-api.json       # ECS task def (API)
│  │  ├─ ecs-task-worker.json    # ECS task def (worker)
│  │  ├─ ecs-service-api.json    # ECS service (API behind ALB)
│  │  ├─ ecs-service-worker.json # ECS service (worker, no ALB)
│  │  ├─ iam-policies/           # IAM role JSONs (S3 read/write, SSM, CloudWatch)
│  │  └─ rds-params.md           # parameter group notes (pg extensions, timeouts)
│  └─ scripts/
│     ├─ build_push_api.sh       # docker build + push to ECR
│     ├─ build_push_worker.sh
│     └─ migrate_db.sh           # run alembic migrations on ECS task
├─ api/
│  ├─ Dockerfile                 # API image
│  ├─ pyproject.toml             # Python deps (poetry or requirements.txt)
│  ├─ requirements.txt
│  ├─ sentra_api/
│  │  ├─ __init__.py
│  │  ├─ main.py                 # FastAPI app entry
│  │  ├─ routes/
│  │  │  ├─ health.py
│  │  │  ├─ leaderboard.py
│  │  │  ├─ timeseries.py
│  │  │  └─ examples.py
│  │  ├─ services/
│  │  │  ├─ sentiment.py         # model load/inference
│  │  │  ├─ queries.py           # DB queries (leaderboard, series)
│  │  │  └─ cache.py             # Redis helpers
│  │  ├─ db/
│  │  │  ├─ base.py              # engine/session
│  │  │  ├─ models.py            # SQLAlchemy models
│  │  │  ├─ schema.sql           # initial schema (optional)
│  │  │  └─ alembic/             # migrations
│  │  └─ util/
│  │     ├─ settings.py          # reads env vars
│  │     └─ logging.py
├─ worker/
│  ├─ Dockerfile                 # Worker image
│  ├─ requirements.txt
│  ├─ flows/                     # Prefect (or Celery) jobs
│  │  ├─ ingest_reddit.py        # fetch posts/comments → S3 + Postgres
│  │  ├─ process_nlp.py          # run sentiment/NER → Postgres
│  │  └─ aggregate_metrics.py    # rollups (15m/1h/1d)
│  └─ worker_entry.py            # starts scheduler/agent
├─ models/
│  ├─ onnx/                      # exported models for fast CPU inference
│  ├─ registry.json              # simple “which model is live” pointer (dev)
│  └─ eval/                      # labeled samples & eval scripts
├─ data/
│  ├─ samples/                   # tiny JSON fixtures for tests
│  └─ schemas/                   # JSON schemas (raw/processed)
├─ notebooks/
│  ├─ exploration.ipynb          # quick EDA, sanity checks
│  └─ eval_baselines.ipynb       # baseline metrics
├─ tests/
│  ├─ test_ticker_detect.py
│  ├─ test_sentiment_service.py
│  └─ test_routes.py
└─ frontend/                     # (optional) if you keep UI in same repo
   ├─ package.json
   ├─ src/
   └─ Dockerfile

