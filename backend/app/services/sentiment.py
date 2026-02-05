import logging
from typing import List, Tuple
from transformers import pipeline

logger = logging.getLogger(__name__)

# Lightweight model for low-memory environments (e.g. EC2 t2.micro with 1GB RAM).
# DistilBERT ~250MB vs RoBERTa-base ~500MB+. Outputs POSITIVE/NEGATIVE; we map
# low-confidence to "neutral" for 3-class API.
LIGHTWEIGHT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
NEUTRAL_THRESHOLD = 0.15  # If score within ±threshold of 0.5, treat as neutral


class SentimentAnalyzer:
    """
    Sentiment analysis service using HuggingFace transformers.
    
    Uses a lightweight DistilBERT model for low-memory (1GB) instances.
    Outputs: positive, negative, or neutral (when confidence is low).
    """
    
    def __init__(self):
        self._classifier = None
        self._is_loaded = False
    
    def load_model(self) -> None:
        """
        Load the sentiment analysis model.
        Should be called once at application startup.
        """
        logger.info("Loading sentiment analysis model (lightweight)...")
        try:
            self._classifier = pipeline(
                "sentiment-analysis",
                model=LIGHTWEIGHT_MODEL,
            )
            self._is_loaded = True
            logger.info("Sentiment analysis model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._is_loaded
    
    def _map_label(self, label: str) -> str:
        """Map model output to lowercase."""
        return label.lower() if label else "neutral"
    
    def _get_top_sentiment(self, result: dict) -> Tuple[str, float]:
        """
        Extract sentiment from model output.
        DistilBERT-SST-2 returns single label (POSITIVE/NEGATIVE) and score.
        We map low confidence to 'neutral' for 3-class API.
        """
        if not result:
            return "neutral", 0.0
        
        label = self._map_label(result.get("label", "neutral"))
        score = round(float(result.get("score", 0.5)), 4)
        
        # Map uncertain predictions to neutral (score near 0.5)
        if abs(score - 0.5) < NEUTRAL_THRESHOLD:
            return "neutral", score
        return label, score
    
    def analyze_single(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Tuple of (sentiment, score)
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If text is empty
        """
        if not self._is_loaded:
            raise RuntimeError("Sentiment model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate very long texts to avoid memory issues
        truncated_text = text[:512] if len(text) > 512 else text
        
        result = self._classifier(truncated_text)
        # Single input returns list of one dict: [{'label': 'POSITIVE', 'score': 0.99}]
        out = result[0] if isinstance(result, list) and result else (result if isinstance(result, dict) else {})
        return self._get_top_sentiment(out)
    
    def analyze_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Analyze sentiment of multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of (sentiment, score) tuples, one per input text
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If texts list is empty
        """
        if not self._is_loaded:
            raise RuntimeError("Sentiment model not loaded. Call load_model() first.")
        
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts and truncate long ones
        processed_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                truncated = text[:512] if len(text) > 512 else text
                processed_texts.append(truncated)
                valid_indices.append(i)
        
        if not processed_texts:
            raise ValueError("All texts are empty")
        
        # Batch inference (returns list of dicts, one per input)
        batch_results = self._classifier(processed_texts)
        
        results = [('neutral', 0.0)] * len(texts)
        for idx, raw in zip(valid_indices, batch_results):
            # Pipeline returns one dict per input: {'label': '...', 'score': ...}
            item = raw if isinstance(raw, dict) else (raw[0] if isinstance(raw, list) and raw else {})
            results[idx] = self._get_top_sentiment(item)
        
        return results


# Global instance (will be initialized in lifespan)
sentiment_analyzer = SentimentAnalyzer()
