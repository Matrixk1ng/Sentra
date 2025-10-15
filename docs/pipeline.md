# NLP Pipeline
Routing:
- If ticker present → FinBERT
- Else → RoBERTa (social sentiment)

Entities:
- Tickers: regex + whitelist map; alias list for company names
- Issues: keyword/phrase lists (economy, housing, climate, immigration, foreign policy)

Store:
- sentiment_score, label, model_name/version, inferred_at

Preprocessing:
- basic cleaning, language filter (en), URL/user/emoji handling
