# Metrics & Aggregations
Windows: 1h, 24h, 7d  
Time-series buckets: 15m/1h  
Metrics: mentions, avg_sentiment, delta vs previous window  
Spike: simple z-score or % change threshold  
Materialize: write to aggregates_* and leaderboards tables on schedule
