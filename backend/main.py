import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, analyze, search
from app.services.sentiment import sentiment_analyzer
from app.services.database import db_service
from app.services.reddit import reddit_service
from app.services.youtube import youtube_service
from app.services.bluesky import bluesky_service
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Loads the sentiment model and initializes services at startup.
    """
    # Startup
    logger.info("Starting Sentra API...")
    
    # Initialize database
    try:
        await db_service.connect()
        logger.info("Database service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize sentiment analyzer
    try:
        sentiment_analyzer.load_model()
        app.state.sentiment_analyzer = sentiment_analyzer
        logger.info("Sentiment analyzer loaded")
    except Exception as e:
        logger.error(f"Failed to initialize sentiment analyzer: {e}")
        app.state.sentiment_analyzer = sentiment_analyzer
    
    # Initialize Reddit service
    try:
        reddit_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize Reddit service: {e}")
    
    # Initialize YouTube service
    try:
        youtube_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize YouTube service: {e}")
    
    # Initialize Bluesky service
    try:
        bluesky_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize Bluesky service: {e}")
    
    logger.info("Sentra API ready to serve requests")


    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down Sentra API...")
    try:
        await db_service.disconnect()
    except Exception as e:
        logger.error(f"Error disconnecting database: {e}")


app = FastAPI(
    title="Sentra API",
    description="Social Media Sentiment Analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://52.0.198.153", "https://sentraai.duckdns.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(search.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Sentra API"}
