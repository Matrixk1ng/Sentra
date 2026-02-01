import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import praw
from praw.exceptions import RedditAPIException, PRAWException
from app.config import get_settings

logger = logging.getLogger(__name__)


class RedditService:
    """
    Reddit data fetching service using PRAW.
    Fetches posts and comments related to a search keyword.
    """
    
    def __init__(self):
        self._reddit: Optional[praw.Reddit] = None
        self._is_configured = False
    
    def initialize(self) -> bool:
        """
        Initialize the Reddit client.
        
        Returns:
            True if successfully configured, False otherwise
        """
        settings = get_settings()
        
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("Reddit API credentials not configured")
            self._is_configured = False
            return False
        
        try:
            self._reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent,
                check_for_async=False,  # We handle async at a higher level
            )
            # Test the connection with a simple request
            self._reddit.read_only = True
            self._is_configured = True
            logger.info("Reddit client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self._is_configured = False
            return False
    
    @property
    def is_configured(self) -> bool:
        """Check if Reddit API is configured."""
        return self._is_configured
    
    def search(self, keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search Reddit for posts and comments matching the keyword.
        
        Args:
            keyword: The search term
            limit: Maximum number of posts to fetch (default 25)
            
        Returns:
            List of normalized post dictionaries
        """
        if not self._is_configured:
            logger.warning("Reddit API not configured, skipping search")
            return []
        
        results = []
        
        try:
            # Search across all subreddits
            submissions = self._reddit.subreddit('all').search(
                keyword,
                sort='relevance',
                time_filter='week',
                limit=limit
            )
            
            for submission in submissions:
                # Add the post itself
                post_text = f"{submission.title}"
                if submission.selftext:
                    post_text += f" {submission.selftext[:500]}"
                
                results.append({
                    'text': post_text[:1000],  # Limit text length
                    'authorName': f"u/{submission.author.name}" if submission.author else "u/[deleted]",
                    'sourceUrl': f"https://reddit.com{submission.permalink}",
                    'createdAt': datetime.fromtimestamp(submission.created_utc),
                })
                
                # Fetch top comments from this post (up to 3 per post)
                try:
                    submission.comments.replace_more(limit=0)  # Don't expand "more comments"
                    for comment in submission.comments[:3]:
                        if hasattr(comment, 'body') and comment.body and len(comment.body) > 20:
                            results.append({
                                'text': comment.body[:1000],
                                'authorName': f"u/{comment.author.name}" if comment.author else "u/[deleted]",
                                'sourceUrl': f"https://reddit.com{comment.permalink}",
                                'createdAt': datetime.fromtimestamp(comment.created_utc),
                            })
                except Exception as e:
                    logger.debug(f"Error fetching comments for submission: {e}")
                    continue
            
            logger.info(f"Fetched {len(results)} items from Reddit for keyword: {keyword}")
            return results
            
        except RedditAPIException as e:
            logger.error(f"Reddit API error: {e}")
            return []
        except PRAWException as e:
            logger.error(f"PRAW error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from Reddit: {e}")
            return []


# Global instance
reddit_service = RedditService()
