from atproto import Client
from app.config import get_settings

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
        
        Args:
            query: The search term
            limit: Maximum number of posts to fetch (default 50)
            
        Returns:
            List of normalized post dictionaries
        """
        if not self._is_configured:
            logger.warning("Bluesky API not configured, skipping search")
            return []
        try:
            response = self.client.app.bsky.feed.search_posts(
                params={"q": query, "limit": min(limit, 100)}  # API max is 100
            )
            bluesky_posts_urls = []
            for post in response.posts:
                bluesky_posts_urls.append(post.uri)
            bluesky_posts_threads = []
            for url in bluesky_posts_urls:
                response = self.client.app.bsky.feed.get_post_thread(
                    params={"uri": url, "depth": 10}
                )
                for post in response.thread:
                    bluesky_posts_threads.append({
                        "text": post.record.text,
                        "authorName": f"@{post.author.handle}",
                        "sourceUrl": url,
                        "source": "bluesky"
                    })
            # Return normalized format (match your YouTube structure)
            return [{
                "text": post.record.text,
                "authorName": f"@{post.author.handle}",
                "sourceUrl": f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}",
                "source": "bluesky"
            } for post in response.posts]
        except Exception as e:
            logger.error(f"Failed to search Bluesky: {e}")
            return []
    
    # For replies/thread
    def get_thread(self, post_uri):
        response = self.client.app.bsky.feed.get_post_thread(
            params={"uri": post_uri, "depth": 10}
        )
        return response.thread