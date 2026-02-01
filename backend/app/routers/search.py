import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Query

from app.models.schemas import (
    SourceType,
    PostResult,
    SentimentSummary,
    SearchResponse,
    DailySentiment,
    HistoryPeriod,
    HistoryResponse,
)
from app.services.database import db_service
from app.services.reddit import reddit_service
from app.services.youtube import youtube_service
from app.services.rate_limiter import rate_limiter, search_cache

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


def _make_cache_key(keyword: str, source: str) -> str:
    """Generate a cache key for search results."""
    return f"search:{keyword.lower()}:{source}"


@router.get("/search", response_model=SearchResponse)
async def search_posts(
    request: Request,
    q: str = Query(..., min_length=1, max_length=100, description="Search keyword"),
    source: SourceType = Query(SourceType.ALL, description="Data source to search"),
):
    """
    Search for posts matching the keyword, analyze sentiment, and store results.
    
    - Fetches posts from Reddit and/or YouTube
    - Runs sentiment analysis on all fetched texts
    - Stores results in the database
    - Updates sentiment history for trend tracking
    - Returns analyzed posts with sentiment scores
    
    Rate limited to 10 searches per minute per keyword.
    Results are cached for 5 minutes.
    """
    keyword = q.strip()
    
    # Check rate limit
    is_allowed, retry_after = rate_limiter.is_allowed(keyword.lower())
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
    
    # Check cache
    cache_key = _make_cache_key(keyword, source.value)
    cached_result = search_cache.get(cache_key)
    if cached_result:
        logger.info(f"Returning cached results for keyword: {keyword}")
        cached_result['cached'] = True
        return SearchResponse(**cached_result)
    
    # Get sentiment analyzer
    analyzer = request.app.state.sentiment_analyzer
    if not analyzer.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model is not yet loaded. Please try again shortly."
        )
    
    # Fetch posts from sources
    raw_posts = []
    errors = []
    
    if source in (SourceType.REDDIT, SourceType.ALL):
        if reddit_service.is_configured:
            try:
                reddit_posts = reddit_service.search(keyword, limit=25)
                for post in reddit_posts:
                    post['source'] = 'reddit'
                raw_posts.extend(reddit_posts)
            except Exception as e:
                logger.error(f"Reddit fetch error: {e}")
                errors.append(f"Reddit: {str(e)}")
        else:
            errors.append("Reddit: API not configured")
    
    if source in (SourceType.YOUTUBE, SourceType.ALL):
        if youtube_service.is_configured:
            try:
                youtube_posts = youtube_service.search(keyword, max_videos=10, comments_per_video=10)
                for post in youtube_posts:
                    post['source'] = 'youtube'
                raw_posts.extend(youtube_posts)
            except Exception as e:
                logger.error(f"YouTube fetch error: {e}")
                errors.append(f"YouTube: {str(e)}")
        else:
            errors.append("YouTube: API not configured")
    
    # Check if we got any posts
    if not raw_posts:
        error_msg = "No posts found."
        if errors:
            error_msg += f" Errors: {'; '.join(errors)}"
        raise HTTPException(status_code=404, detail=error_msg)
    
    # Run sentiment analysis
    try:
        texts = [post['text'] for post in raw_posts]
        sentiment_results = analyzer.analyze_batch(texts)
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze sentiment")
    
    # Combine posts with sentiment results
    analyzed_posts = []
    for post, (sentiment, score) in zip(raw_posts, sentiment_results):
        analyzed_posts.append({
            **post,
            'sentiment': sentiment,
            'score': score,
        })
    
    # Store in database
    try:
        search_id = await db_service.create_search(keyword)
        post_ids = await db_service.create_posts(search_id, analyzed_posts)
        
        # Update post IDs
        for post, post_id in zip(analyzed_posts, post_ids):
            post['id'] = post_id
        
        # Update sentiment history
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for post in analyzed_posts:
            sentiment_counts[post['sentiment']] += 1
        
        await db_service.upsert_sentiment_history(
            keyword=keyword,
            target_date=date.today(),
            positive_count=sentiment_counts['positive'],
            negative_count=sentiment_counts['negative'],
            neutral_count=sentiment_counts['neutral'],
        )
    except Exception as e:
        logger.error(f"Database error: {e}")
        # Continue even if DB fails - return results without persistence
        search_id = "temp_" + str(int(datetime.utcnow().timestamp()))
        for i, post in enumerate(analyzed_posts):
            post['id'] = f"{search_id}_{i}"
    
    # Build response
    summary = SentimentSummary(
        total=len(analyzed_posts),
        positive=sum(1 for p in analyzed_posts if p['sentiment'] == 'positive'),
        negative=sum(1 for p in analyzed_posts if p['sentiment'] == 'negative'),
        neutral=sum(1 for p in analyzed_posts if p['sentiment'] == 'neutral'),
    )
    
    post_results = [
        PostResult(
            id=post['id'],
            text=post['text'],
            source=post['source'],
            sentiment=post['sentiment'],
            score=post['score'],
            authorName=post.get('authorName'),
            sourceUrl=post.get('sourceUrl'),
            createdAt=post.get('createdAt', datetime.utcnow()),
        )
        for post in analyzed_posts
    ]
    
    # Sort by score (highest first)
    post_results.sort(key=lambda p: p.score, reverse=True)
    
    response_data = {
        'searchId': search_id,
        'keyword': keyword,
        'source': source.value,
        'posts': post_results,
        'summary': summary,
        'fetchedAt': datetime.utcnow(),
        'cached': False,
    }
    
    # Cache the result
    search_cache.set(cache_key, {
        'searchId': search_id,
        'keyword': keyword,
        'source': source.value,
        'posts': [p.model_dump() for p in post_results],
        'summary': summary.model_dump(),
        'fetchedAt': response_data['fetchedAt'].isoformat(),
        'cached': True,
    })
    
    return SearchResponse(**response_data)


@router.get("/history", response_model=HistoryResponse)
async def get_sentiment_history(
    q: str = Query(..., min_length=1, max_length=100, description="Search keyword"),
    days: int = Query(7, ge=1, le=90, description="Number of days of history"),
):
    """
    Get historical sentiment data for a keyword.
    
    Returns aggregated sentiment counts per day for building trend charts.
    """
    keyword = q.strip()
    
    try:
        history_data = await db_service.get_history(keyword, days)
    except Exception as e:
        logger.error(f"Database error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history data")
    
    # Build date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    # Convert to response format
    daily_sentiments = [
        DailySentiment(
            date=item['date'],
            positive=item['positive'],
            negative=item['negative'],
            neutral=item['neutral'],
        )
        for item in history_data
    ]
    
    return HistoryResponse(
        keyword=keyword,
        period=HistoryPeriod(
            start=start_date.isoformat(),
            end=end_date.isoformat(),
        ),
        data=daily_sentiments,
    )
