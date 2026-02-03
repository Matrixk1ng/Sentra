from atproto import Client
import logging
from app.config import get_settings
logger = logging.getLogger(__name__)

class BlueskyService:
    """
    Bluesky data fetching service using the official API.
    Fetches posts and comments related to a search keyword.
    """
    def __init__(self):
        self._client = None
        self._is_configured = False

    def initialize(self) -> bool:
        """
        Initialize the Bluesky client.
        
        Returns:
            True if successfully configured, False otherwise
        """
        settings = get_settings()

        if not settings.bluesky_handle or not settings.bluesky_app_password:
            logger.warning("Bluesky credentials not configured")
            self._is_configured = False
            return False
        try:
            self._client = Client()
            self._client.login(settings.bluesky_handle, settings.bluesky_app_password)
            self._is_configured = True
            logger.info("Bluesky client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Bluesky client: {e}")
            self._is_configured = False
            return False
    
    @property
    def is_configured(self) -> bool:
        """Check if bluesky API is configured."""
        return self._is_configured

    def search(self, query, limit=50):
        """
        Search Bluesky for posts related to a search keyword.
        """
        if not self._is_configured:
            logger.warning("Bluesky API not configured, skipping search")
            return []
         
        results = []
        try:
            response = self._client.app.bsky.feed.search_posts(
                params={"q": query, "limit": min(limit, 100), "lang": "en"}
            )
            
            for post in response.posts:
                # Add the main post
                results.append({
                    "text": post.record.text,
                    "authorName": f"@{post.author.handle}",
                    "sourceUrl": f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}",
                    "createdAt": getattr(post.record, 'created_at', None),
                    "source": "bluesky"
                })
                
                # Fetch replies for this post
                try:
                    thread_response = self._client.app.bsky.feed.get_post_thread(
                        params={"uri": post.uri, "depth": 5}
                    )
                    thread = thread_response.thread
                    
                    if hasattr(thread, 'replies') and thread.replies:
                        for reply in thread.replies:
                            if reply is None:
                                continue
                            if hasattr(reply, 'notFound') or hasattr(reply, 'blocked'):
                                continue
                            if hasattr(reply, 'post'):
                                results.append({
                                    "text": reply.post.record.text,
                                    "authorName": f"@{reply.post.author.handle}",
                                    "sourceUrl": f"https://bsky.app/profile/{reply.post.author.handle}/post/{reply.post.uri.split('/')[-1]}",
                                    "createdAt": getattr(reply.post.record, 'created_at', None),
                                    "source": "bluesky"
                                })
                except Exception as e:
                    logger.debug(f"Could not fetch thread for {post.uri}: {e}")
                    continue
            
            logger.info(f"Fetched {len(results)} posts/replies from Bluesky for keyword: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Failed to search Bluesky: {e}")
            return []

bluesky_service = BlueskyService()