import logging
from typing import List, Tuple
from transformers import pipeline

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analysis service using HuggingFace transformers.
    
    Uses the cardiffnlp/twitter-roberta-base-sentiment-latest model
    which outputs: positive, negative, neutral labels with confidence scores.
    """
    
    def __init__(self):
        self._classifier = None
        self._is_loaded = False
    
    def load_model(self) -> None:
        """
        Load the sentiment analysis model.
        Should be called once at application startup.
        """
        logger.info("Loading sentiment analysis model...")
        try:
            self._classifier = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                top_k=None  # Return all labels with scores
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
        """
        Map model output labels to standard format.
        The model outputs: 'positive', 'negative', 'neutral'
        """
        label_lower = label.lower()
        if label_lower in ['positive', 'negative', 'neutral']:
            return label_lower
        # Fallback mapping for any unexpected labels
        return 'neutral'
    
    def _get_top_sentiment(self, results: List[dict]) -> Tuple[str, float]:
        """
        Extract the top sentiment and its score from model output.
        
        Args:
            results: List of dicts with 'label' and 'score' keys
            
        Returns:
            Tuple of (sentiment_label, score)
        """
        if not results:
            return 'neutral', 0.0
        
        # Results are already sorted by score (highest first)
        top_result = results[0]
        sentiment = self._map_label(top_result['label'])
        score = round(top_result['score'], 4)
        return sentiment, score
    
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
        
        results = self._classifier(truncated_text)
        # Results is a list containing a list of label/score dicts
        return self._get_top_sentiment(results[0] if results else [])
    
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
        
        # Batch inference
        batch_results = self._classifier(processed_texts)
        
        # Map results back, filling in neutral for empty texts
        results = [('neutral', 0.0)] * len(texts)
        for idx, result in zip(valid_indices, batch_results):
            results[idx] = self._get_top_sentiment(result)
        
        return results


# Global instance (will be initialized in lifespan)
sentiment_analyzer = SentimentAnalyzer()
