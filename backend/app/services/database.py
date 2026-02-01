import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import asyncpg
from app.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Async database operations using asyncpg.
    Handles all CRUD operations for searches, posts, and sentiment history.
    """
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Initialize the database connection pool."""
        settings = get_settings()
        try:
            self._pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=10,
            )
            logger.info("Database connection pool created")
            await self._ensure_tables()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")
    
    async def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        async with self._pool.acquire() as conn:
            # Create Search table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "Search" (
                    id TEXT PRIMARY KEY,
                    keyword TEXT NOT NULL,
                    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create Post table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "Post" (
                    id TEXT PRIMARY KEY,
                    "searchId" TEXT NOT NULL REFERENCES "Search"(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    score FLOAT NOT NULL,
                    "authorName" TEXT,
                    "sourceUrl" TEXT,
                    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create index on searchId
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_post_search_id ON "Post"("searchId")
            """)
            
            # Create SentimentHistory table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "SentimentHistory" (
                    id TEXT PRIMARY KEY,
                    keyword TEXT NOT NULL,
                    date DATE NOT NULL,
                    "positiveCount" INTEGER NOT NULL DEFAULT 0,
                    "negativeCount" INTEGER NOT NULL DEFAULT 0,
                    "neutralCount" INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(keyword, date)
                )
            """)
            
            logger.info("Database tables ensured")
    
    def _generate_id(self) -> str:
        """Generate a cuid-like ID."""
        import time
        import random
        import string
        timestamp = hex(int(time.time() * 1000))[2:]
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"c{timestamp}{random_part}"
    
    async def create_search(self, keyword: str) -> str:
        """
        Create a new search record.
        
        Args:
            keyword: The search keyword
            
        Returns:
            The generated search ID
        """
        search_id = self._generate_id()
        async with self._pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO "Search" (id, keyword) VALUES ($1, $2)',
                search_id, keyword
            )
        logger.info(f"Created search record: {search_id} for keyword: {keyword}")
        return search_id
    
    async def create_posts(self, search_id: str, posts: List[Dict[str, Any]]) -> List[str]:
        """
        Bulk insert posts for a search.
        
        Args:
            search_id: The search ID to associate posts with
            posts: List of post dictionaries with keys:
                   text, source, sentiment, score, authorName, sourceUrl, createdAt
                   
        Returns:
            List of generated post IDs
        """
        if not posts:
            return []
        
        post_ids = []
        async with self._pool.acquire() as conn:
            # Prepare bulk insert
            records = []
            for post in posts:
                post_id = self._generate_id()
                post_ids.append(post_id)
                records.append((
                    post_id,
                    search_id,
                    post['text'],
                    post['source'],
                    post['sentiment'],
                    post['score'],
                    post.get('authorName'),
                    post.get('sourceUrl'),
                    post.get('createdAt', datetime.utcnow()),
                ))
            
            await conn.executemany(
                '''INSERT INTO "Post" 
                   (id, "searchId", text, source, sentiment, score, "authorName", "sourceUrl", "createdAt")
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)''',
                records
            )
        
        logger.info(f"Inserted {len(posts)} posts for search {search_id}")
        return post_ids
    
    async def upsert_sentiment_history(
        self, 
        keyword: str, 
        target_date: date,
        positive_count: int,
        negative_count: int,
        neutral_count: int
    ) -> None:
        """
        Insert or update sentiment history for a keyword on a date.
        If record exists, adds to existing counts.
        
        Args:
            keyword: The search keyword
            target_date: The date for the history record
            positive_count: Number of positive posts
            negative_count: Number of negative posts
            neutral_count: Number of neutral posts
        """
        history_id = self._generate_id()
        async with self._pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO "SentimentHistory" 
                    (id, keyword, date, "positiveCount", "negativeCount", "neutralCount")
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (keyword, date) DO UPDATE SET
                    "positiveCount" = "SentimentHistory"."positiveCount" + EXCLUDED."positiveCount",
                    "negativeCount" = "SentimentHistory"."negativeCount" + EXCLUDED."negativeCount",
                    "neutralCount" = "SentimentHistory"."neutralCount" + EXCLUDED."neutralCount"
            ''', history_id, keyword, target_date, positive_count, negative_count, neutral_count)
        
        logger.info(f"Upserted sentiment history for {keyword} on {target_date}")
    
    async def get_history(
        self, 
        keyword: str, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get sentiment history for a keyword over the specified number of days.
        
        Args:
            keyword: The search keyword
            days: Number of days to look back (default 7)
            
        Returns:
            List of daily sentiment counts
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT date, "positiveCount", "negativeCount", "neutralCount"
                FROM "SentimentHistory"
                WHERE keyword = $1 AND date >= $2 AND date <= $3
                ORDER BY date ASC
            ''', keyword, start_date, end_date)
        
        # Convert to list of dicts
        result = []
        for row in rows:
            result.append({
                'date': row['date'].isoformat(),
                'positive': row['positiveCount'],
                'negative': row['negativeCount'],
                'neutral': row['neutralCount'],
            })
        
        return result
    
    async def get_recent_search(self, keyword: str, minutes: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get a recent search for caching purposes.
        
        Args:
            keyword: The search keyword
            minutes: How recent the search should be
            
        Returns:
            Search record with posts if found, None otherwise
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        async with self._pool.acquire() as conn:
            search = await conn.fetchrow('''
                SELECT id, keyword, "createdAt"
                FROM "Search"
                WHERE keyword = $1 AND "createdAt" > $2
                ORDER BY "createdAt" DESC
                LIMIT 1
            ''', keyword, cutoff)
            
            if not search:
                return None
            
            posts = await conn.fetch('''
                SELECT id, text, source, sentiment, score, "authorName", "sourceUrl", "createdAt"
                FROM "Post"
                WHERE "searchId" = $1
                ORDER BY score DESC
            ''', search['id'])
        
        return {
            'searchId': search['id'],
            'keyword': search['keyword'],
            'createdAt': search['createdAt'],
            'posts': [dict(p) for p in posts],
        }


# Global instance
db_service = DatabaseService()
