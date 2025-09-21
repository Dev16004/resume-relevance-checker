"""
Embedding Service for Resume Checker Application

This module provides functionality to generate embeddings for text using
HuggingFace sentence-transformers models for semantic similarity search.
"""

import os
import logging
from typing import List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from config import get_embedding_model_config, get_available_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self, model_key: str = None):
        """
        Initialize the embedding service with a pre-trained model
        
        Args:
            model_key: Configuration key for the model to use (fast, balanced, high_quality, multilingual)
                      If None, uses the default model from config
        """
        self.model_config = get_embedding_model_config(model_key)
        self.model_name = self.model_config["name"]
        self.model_key = model_key or "fast"
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Embedding service initialized with device: {self.device}")
        logger.info(f"Model configuration: {self.model_key} - {self.model_config['description']}")
        
    def _load_model(self):
        """Lazy load the model when first needed"""
        if self.model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name, device=self.device)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        self._load_model()
        return self.model.get_sentence_embedding_dimension()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array containing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(self.get_embedding_dimension())
        
        self._load_model()
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
            
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return np.zeros(self.get_embedding_dimension())
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batch (more efficient)
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of numpy arrays containing embedding vectors
        """
        if not texts:
            return []
        
        self._load_model()
        
        try:
            # Clean and preprocess texts
            cleaned_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings in batch
            embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True, batch_size=32)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return [emb for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [np.zeros(self.get_embedding_dimension()) for _ in texts]
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding generation
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate very long texts (models have token limits)
        max_length = 512  # Conservative limit for most models
        if len(text.split()) > max_length:
            text = " ".join(text.split()[:max_length])
            logger.debug(f"Text truncated to {max_length} words")
        
        return text
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            # Ensure result is between 0 and 1
            similarity = max(0.0, min(1.0, (similarity + 1) / 2))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: List[np.ndarray],
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar embeddings to a query embedding
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity
        """
        if not candidate_embeddings:
            return []
        
        similarities = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate_emb)
            similarities.append((i, similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_model_info(self):
        """Get information about the current model"""
        return {
            "model_key": self.model_key,
            "model_name": self.model_name,
            "description": self.model_config["description"],
            "dimensions": self.model_config["dimensions"],
            "performance": self.model_config["performance"],
            "quality": self.model_config["quality"],
            "device": self.device
        }
    
    def get_current_model(self):
        """Get the current model key"""
        return self.model_key
    
    def switch_model(self, model_key: str):
        """
        Switch to a different embedding model
        
        Args:
            model_key: Configuration key for the new model
        """
        logger.info(f"Switching from {self.model_key} to {model_key}")
        self.model_config = get_embedding_model_config(model_key)
        self.model_name = self.model_config["name"]
        self.model_key = model_key
        self.model = None  # Force reload on next use
        logger.info(f"Model switched to: {self.model_key} - {self.model_config['description']}")
    
    @staticmethod
    def get_available_models() -> dict:
        """Get all available embedding models"""
        return get_available_models()

# Global instance for easy access
embedding_service = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    return embedding_service