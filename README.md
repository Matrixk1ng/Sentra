# Sentra

A social media sentiment analysis dashboard that aggregates posts from Reddit and YouTube, analyzes sentiment using AI, and visualizes trends in real-time.

## Features

- **Multi-platform Analysis** – Fetch posts from Reddit and YouTube comments
- **AI-Powered Sentiment** – Uses HuggingFace's RoBERTa model for accurate classification
- **Interactive Dashboard** – Pie charts, trend lines, and filterable post lists
- **Historical Tracking** – View sentiment changes over time
- **Rate Limiting & Caching** – Built-in protections against API abuse

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| AI/NLP | distilbert-base-uncased-finetuned-sst-2-english |
| Charts | Recharts |
| Containerization | Docker & Docker Compose |

---

## Setup

### Prerequisites


- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Git](https://git-scm.com/downloads)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/Sentra.git
cd Sentra
```

### Step 2: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API credentials:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/sentra
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=sentra:v1.0.0
YOUTUBE_API_KEY=your_youtube_api_key
```

### Step 3: Get API Credentials

#### Reddit API (Free)

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: Sentra
   - **App type**: Select "script"
   - **Redirect URI**: http://localhost:8000
4. Click "Create app"
5. Copy the **client ID** (under the app name) and **secret**

#### YouTube Data API (Free - 10,000 units/day)

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the "YouTube Data API v3"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key

> **Note**: The app works without API keys, but you won't be able to fetch data from those sources.

### Step 4: Build and Start Services

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Build and start the FastAPI backend (downloads AI model on first run ~500MB)
- Build and start the Next.js frontend

**First startup takes 5-10 minutes** due to:
- Downloading the sentiment analysis model
- Installing dependencies
- Building the frontend

### Step 5: Initialize the Database

Once services are running, run Prisma migrations:

```bash
docker-compose exec frontend npx prisma db push
```

### Step 6: Verify Setup

Open your browser and check:

| Service | URL | Expected |
|---------|-----|----------|
| Frontend | http://localhost:3000 | Dashboard UI |
| Backend Health | http://localhost:8000/health | JSON with status |
| API Docs | http://localhost:8000/docs | Swagger UI |

The health endpoint should show:
```json
{
  "status": "ok",
  "database": "connected",
  "sentimentModel": "loaded",
  "reddit": "configured",
  "youtube": "configured"
}
```

---

## Usage

1. **Search**: Enter a keyword (e.g., "ChatGPT", "climate change", "Tesla")
2. **Select Source**: Choose Reddit, YouTube, or All
3. **Analyze**: View sentiment distribution and individual posts
4. **Filter**: Filter posts by sentiment type
5. **Track**: Search the same keyword over time to build history

---

## Development

### Running Locally (without Docker)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npx prisma generate
npm run dev
```

### Useful Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build
```

### Database Management

```bash
# Open Prisma Studio (GUI for database)
docker-compose exec frontend npx prisma studio

# Reset database
docker-compose exec frontend npx prisma db push --force-reset
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/analyze` | POST | Analyze single text |
| `/analyze/batch` | POST | Analyze multiple texts |
| `/search` | GET | Search and analyze from sources |
| `/history` | GET | Get historical sentiment data |

### Example API Calls

```bash
# Health check
curl http://localhost:8000/health

# Analyze single text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

# Search Reddit for a keyword
curl "http://localhost:8000/search?q=python&source=reddit"

# Get 7-day history
curl "http://localhost:8000/history?q=python&days=7"
```

---

## Troubleshooting

### "Sentiment model not loaded"

The model downloads on first startup. Wait a few minutes and check logs:
```bash
docker-compose logs -f backend
```

### "Database connection failed"

Ensure PostgreSQL is running:
```bash
docker-compose ps
```

### "Reddit/YouTube not configured"

Add API credentials to `.env` and restart:
```bash
docker-compose down
docker-compose up
```

### Frontend not connecting to backend

Check that `NEXT_PUBLIC_API_URL` is set in `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Port already in use

Stop other services using the ports or change ports in `docker-compose.yml`:
- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432

---

## Project Structure

```
sentra/
├── docker-compose.yml      # Container orchestration
├── .env.example            # Environment template
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # Pages and API routes
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and API client
│   │   └── types/         # TypeScript types
│   └── prisma/            # Database schema
└── backend/                # FastAPI application
    ├── main.py            # Application entry
    └── app/
        ├── routers/       # API endpoints
        ├── services/      # Business logic
        └── models/        # Pydantic schemas
```

---

## License

MIT License - feel free to use this project for learning or commercial purposes.
