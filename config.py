"""
Configuration settings for the Resume Checker Application
"""

import os
from typing import Dict, Any

# Embedding Model Configurations
EMBEDDING_MODELS = {
    "fast": {
        "name": "all-MiniLM-L6-v2",
        "description": "Fast and lightweight model, good for quick processing",
        "dimensions": 384,
        "performance": "Fast",
        "quality": "Good"
    },
    "balanced": {
        "name": "all-mpnet-base-v2",
        "description": "Balanced performance and quality",
        "dimensions": 768,
        "performance": "Medium",
        "quality": "High"
    },
    "high_quality": {
        "name": "sentence-transformers/all-roberta-large-v1",
        "description": "High quality embeddings, slower processing",
        "dimensions": 1024,
        "performance": "Slow",
        "quality": "Very High"
    },
    "multilingual": {
        "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "description": "Supports multiple languages",
        "dimensions": 384,
        "performance": "Medium",
        "quality": "Good"
    }
}

# Default model configuration
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "fast")

# Database configuration
DATABASE_CONFIG = {
    "name": "resume_checker.db",
    "path": os.path.join(os.path.dirname(__file__), "resume_checker.db")
}

# Upload configuration
UPLOAD_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": [".pdf", ".docx", ".txt"],
    "upload_folder": os.path.join(os.path.dirname(__file__), "uploads")
}

# API configuration
API_CONFIG = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": os.getenv("DEBUG", "False").lower() == "true"
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "Resume Checker",
    "page_icon": "📄",
    "layout": "wide"
}

def get_embedding_model_config(model_key: str = None) -> Dict[str, Any]:
    """
    Get embedding model configuration
    
    Args:
        model_key: Key for the model configuration (fast, balanced, high_quality, multilingual)
                  If None, uses DEFAULT_EMBEDDING_MODEL
    
    Returns:
        Dictionary containing model configuration
    """
    if model_key is None:
        model_key = DEFAULT_EMBEDDING_MODEL
    
    if model_key not in EMBEDDING_MODELS:
        raise ValueError(f"Unknown model key: {model_key}. Available: {list(EMBEDDING_MODELS.keys())}")
    
    return EMBEDDING_MODELS[model_key]

def get_available_models() -> Dict[str, Dict[str, Any]]:
    """Get all available embedding models"""
    return EMBEDDING_MODELS.copy()