from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Supported data sources."""
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    ALL = "all"


class AnalyzeRequest(BaseModel):
    """Request model for single text sentiment analysis."""
    text: str = Field(..., min_length=1, description="Text to analyze")


class AnalyzeResponse(BaseModel):
    """Response model for single text sentiment analysis."""
    text: str
    sentiment: str  # "positive" | "negative" | "neutral"
    score: float = Field(..., ge=0, le=1)
    processingTimeMs: int


class BatchAnalyzeRequest(BaseModel):
    """Request model for batch sentiment analysis."""
    texts: List[str] = Field(..., min_length=1, description="List of texts to analyze")


class SentimentResult(BaseModel):
    """Individual sentiment result in a batch response."""
    text: str
    sentiment: str  # "positive" | "negative" | "neutral"
    score: float = Field(..., ge=0, le=1)


class BatchAnalyzeResponse(BaseModel):
    """Response model for batch sentiment analysis."""
    results: List[SentimentResult]
    totalProcessingTimeMs: int
    count: int


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str


# Search endpoint models
class PostResult(BaseModel):
    """Individual post result from search."""
    id: str
    text: str
    source: str  # "reddit" | "youtube"
    sentiment: str  # "positive" | "negative" | "neutral"
    score: float = Field(..., ge=0, le=1)
    authorName: Optional[str] = None
    sourceUrl: Optional[str] = None
    createdAt: datetime


class SentimentSummary(BaseModel):
    """Aggregated sentiment counts."""
    total: int
    positive: int
    negative: int
    neutral: int


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    searchId: str
    keyword: str
    source: str
    posts: List[PostResult]
    summary: SentimentSummary
    fetchedAt: datetime
    cached: bool = False


# History endpoint models
class DailySentiment(BaseModel):
    """Daily sentiment data point."""
    date: str
    positive: int
    negative: int
    neutral: int


class HistoryPeriod(BaseModel):
    """Time period for history query."""
    start: str
    end: str


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""
    keyword: str
    period: HistoryPeriod
    data: List[DailySentiment]
