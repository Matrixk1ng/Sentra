# API (FastAPI) — JSON only
GET /leaderboard?mode=stocks|politics&window=24h
→ [{entity, rank, mentions, delta, avg_sent, example_count}]

GET /series?q=<entity>&metric=mentions|sentiment&window=7d&bucket=1h
→ [{t, value}]

GET /examples?q=<entity>&limit=20&sentiment=pos|neg|any
→ [{post_id, title, subreddit, url, label, score, created_at}]

GET /search?q=<entity>
→ {exists, quick_stats}

GET /health → {status:"ok"}
