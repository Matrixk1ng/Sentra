import logging
import time
from collections import defaultdict
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RateLimitEntry:
    """Entry for tracking rate limit state."""
    request_count: int
    window_start: float


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks requests per keyword within a time window.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._entries: Dict[str, RateLimitEntry] = defaultdict(
            lambda: RateLimitEntry(request_count=0, window_start=time.time())
        )
    
    def is_allowed(self, key: str) -> Tuple[bool, Optional[int]]:
        """
        Check if a request is allowed for the given key.
        
        Args:
            key: The rate limit key (e.g., keyword)
            
        Returns:
            Tuple of (is_allowed, seconds_until_reset)
        """
        current_time = time.time()
        entry = self._entries[key]
        
        # Check if window has expired
        if current_time - entry.window_start >= self._window_seconds:
            # Reset the window
            self._entries[key] = RateLimitEntry(
                request_count=1,
                window_start=current_time
            )
            return True, None
        
        # Check if within rate limit
        if entry.request_count < self._max_requests:
            entry.request_count += 1
            return True, None
        
        # Rate limited
        seconds_until_reset = int(self._window_seconds - (current_time - entry.window_start))
        return False, seconds_until_reset
    
    def reset(self, key: str) -> None:
        """Reset the rate limit for a key."""
        if key in self._entries:
            del self._entries[key]


class SearchCache:
    """
    Simple in-memory cache for search results.
    Caches results to avoid redundant API calls.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize the cache.
        
        Args:
            ttl_seconds: Time-to-live for cached entries (default 5 minutes)
        """
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, dict]] = {}
    
    def get(self, key: str) -> Optional[dict]:
        """
        Get a cached value if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key not in self._cache:
            return None
        
        timestamp, value = self._cache[key]
        if time.time() - timestamp > self._ttl_seconds:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: dict) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (time.time(), value)
    
    def invalidate(self, key: str) -> None:
        """Remove an entry from the cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Global instances
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
search_cache = SearchCache(ttl_seconds=300)  # 5 minutes
