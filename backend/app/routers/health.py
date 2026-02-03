from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings, Settings
from app.services.reddit import reddit_service
from app.services.youtube import youtube_service
from app.services.bluesky import bluesky_service

router = APIRouter(tags=["health"])


async def check_database_connection(settings: Settings) -> bool:
    """Check if the database is reachable."""
    try:
        # Convert postgresql:// to postgresql+asyncpg://
        async_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        engine = create_async_engine(async_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception:
        return False


@router.get("/health")
async def health_check(request: Request, settings: Settings = Depends(get_settings)):
    """Health check endpoint that verifies all service statuses."""
    db_connected = await check_database_connection(settings)
    
    # Check sentiment model status
    model_loaded = False
    if hasattr(request.app.state, 'sentiment_analyzer'):
        model_loaded = request.app.state.sentiment_analyzer.is_loaded
    
    return {
        "status": "ok",
        "database": "connected" if db_connected else "disconnected",
        "sentimentModel": "loaded" if model_loaded else "not_loaded",
        "reddit": "configured" if reddit_service.is_configured else "not_configured",
        "youtube": "configured" if youtube_service.is_configured else "not_configured",
        "bluesky": "configured" if bluesky_service.is_configured else "not_configured",
    }
