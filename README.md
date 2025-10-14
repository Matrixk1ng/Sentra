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
