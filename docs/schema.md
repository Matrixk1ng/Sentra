# Logical Schema (conceptual)
posts(id, subreddit, title, body, url, score, num_comments, created_at)
comments(id, post_id, body, score, created_at)
post_nlp(post_id, sentiment_score, label, model_version, inferred_at)
entities(post_id, entity_type[TICKER|ISSUE], value, confidence)
aggregates_mentions(time_bucket, entity, count, subreddit)
aggregates_sentiment(time_bucket, entity, avg_sent, subreddit)
leaderboards(window, entity, mentions, delta, avg_sent, rank)

Indexes planned:
- posts(created_at), entities(value), aggregates_* (time_bucket, entity)
Time buckets: 15m, 1h, 24h
