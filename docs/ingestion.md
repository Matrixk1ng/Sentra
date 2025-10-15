# Ingestion (Reddit / PRAW)
Subs (MVP): r/wallstreetbets, r/stocks, r/investing, r/politics  
Frequency: every 5–10m; limit posts/run; comments per post (cap).  
Fields: id, subreddit, title, selftext, url, score, num_comments, created_utc  
Dedupe: skip IDs already seen  
Backoff: exponential on rate-limit  
(Optional raw S3): reddit/raw/<sub>/<YYYY-MM-DD>/post_<id>.json
