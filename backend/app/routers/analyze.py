import time
import logging
from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    SentimentResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["sentiment"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_single(request: Request, body: AnalyzeRequest):
    """
    Analyze sentiment of a single text.
    
    Returns the sentiment (positive/negative/neutral) and confidence score.
    """
    analyzer = request.app.state.sentiment_analyzer
    
    if not analyzer.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model is not yet loaded. Please try again shortly."
        )
    
    try:
        start_time = time.perf_counter()
        sentiment, score = analyzer.analyze_single(body.text)
        processing_time = int((time.perf_counter() - start_time) * 1000)
        
        return AnalyzeResponse(
            text=body.text,
            sentiment=sentiment,
            score=score,
            processingTimeMs=processing_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze text")


@router.post("/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(request: Request, body: BatchAnalyzeRequest):
    """
    Analyze sentiment of multiple texts in a batch.
    
    More efficient than calling /analyze multiple times.
    """
    analyzer = request.app.state.sentiment_analyzer
    
    if not analyzer.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model is not yet loaded. Please try again shortly."
        )
    
    # Validate batch size
    max_batch_size = 100
    if len(body.texts) > max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum of {max_batch_size} texts"
        )
    
    # Validate each text is non-empty
    empty_indices = [i for i, t in enumerate(body.texts) if not t or not t.strip()]
    if empty_indices:
        raise HTTPException(
            status_code=400,
            detail=f"Empty texts found at indices: {empty_indices[:5]}{'...' if len(empty_indices) > 5 else ''}"
        )
    
    try:
        start_time = time.perf_counter()
        results = analyzer.analyze_batch(body.texts)
        processing_time = int((time.perf_counter() - start_time) * 1000)
        
        sentiment_results = [
            SentimentResult(
                text=text,
                sentiment=sentiment,
                score=score,
            )
            for text, (sentiment, score) in zip(body.texts, results)
        ]
        
        return BatchAnalyzeResponse(
            results=sentiment_results,
            totalProcessingTimeMs=processing_time,
            count=len(sentiment_results),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing batch: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze texts")
