import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import get_settings

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    YouTube data fetching service using the official API.
    Fetches video comments related to a search keyword.
    """
    
    def __init__(self):
        self._youtube = None
        self._is_configured = False
    
    def initialize(self) -> bool:
        """
        Initialize the YouTube client.
        
        Returns:
            True if successfully configured, False otherwise
        """
        settings = get_settings()
        
        if not settings.youtube_api_key:
            logger.warning("YouTube API key not configured")
            self._is_configured = False
            return False
        
        try:
            self._youtube = build(
                'youtube', 
                'v3', 
                developerKey=settings.youtube_api_key,
                cache_discovery=False
            )
            self._is_configured = True
            logger.info("YouTube client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {e}")
            self._is_configured = False
            return False
    
    @property
    def is_configured(self) -> bool:
        """Check if YouTube API is configured."""
        return self._is_configured
    
    def _parse_datetime(self, date_string: str) -> datetime:
        """Parse YouTube API datetime string."""
        try:
            # YouTube returns ISO 8601 format
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception:
            return datetime.utcnow()
    
    def search(self, keyword: str, max_videos: int = 10, comments_per_video: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos and fetch their comments.
        
        Args:
            keyword: The search term
            max_videos: Maximum number of videos to search (default 10)
            comments_per_video: Maximum comments per video (default 10)
            
        Returns:
            List of normalized comment dictionaries
            
        Note:
            - 1 search request = 100 quota units
            - 1 commentThreads request = 1 quota unit
            - Daily free quota = 10,000 units
        """
        if not self._is_configured:
            logger.warning("YouTube API not configured, skipping search")
            return []
        
        results = []
        
        try:
            # Search for videos (100 quota units)
            search_response = self._youtube.search().list(
                q=keyword,
                part='id,snippet',
                type='video',
                maxResults=max_videos,
                order='relevance',
                relevanceLanguage='en',
            ).execute()
            
            video_ids = []
            video_info = {}
            
            for item in search_response.get('items', []):
                video_id = item['id'].get('videoId')
                if video_id:
                    video_ids.append(video_id)
                    video_info[video_id] = {
                        'title': item['snippet']['title'],
                        'channelTitle': item['snippet']['channelTitle'],
                    }
            
            # Fetch comments for each video (1 quota unit each)
            for video_id in video_ids:
                try:
                    comments_response = self._youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=comments_per_video,
                        order='relevance',
                        textFormat='plainText',
                    ).execute()
                    
                    for item in comments_response.get('items', []):
                        comment = item['snippet']['topLevelComment']['snippet']
                        comment_text = comment.get('textDisplay', '')
                        
                        if comment_text and len(comment_text) > 10:
                            results.append({
                                'text': comment_text[:1000],  # Limit text length
                                'authorName': comment.get('authorDisplayName', 'Unknown'),
                                'sourceUrl': f"https://www.youtube.com/watch?v={video_id}",
                                'createdAt': self._parse_datetime(comment.get('publishedAt', '')),
                            })
                            
                except HttpError as e:
                    if e.resp.status == 403:
                        # Comments might be disabled for this video
                        logger.debug(f"Comments disabled for video {video_id}")
                    else:
                        logger.warning(f"Error fetching comments for video {video_id}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing video {video_id}: {e}")
                    continue
            
            logger.info(f"Fetched {len(results)} comments from YouTube for keyword: {keyword}")
            return results
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("YouTube API quota exceeded or access denied")
            else:
                logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from YouTube: {e}")
            return []


# Global instance
youtube_service = YouTubeService()
