from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/sentra"
    
    # Reddit API
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "sentra:v1.0.0"
    
    # YouTube API
    youtube_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
