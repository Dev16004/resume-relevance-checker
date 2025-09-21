"""
Vector Store Service for Resume Checker Application

This module provides functionality to store and query embeddings using ChromaDB
for efficient semantic similarity search.
"""

import os
import logging
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from embedding_service import get_embedding_service

# Try to import ChromaDB, fallback to mock implementation if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Service for storing and querying embeddings using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.client = None
        self.embedding_service = get_embedding_service()
        
        # Collection names
        self.RESUME_COLLECTION = "resumes"
        self.JOB_DESCRIPTION_COLLECTION = "job_descriptions"
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            if not CHROMADB_AVAILABLE:
                logger.warning("ChromaDB not available, using fallback mode")
                self.client = None
                return
                
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(f"ChromaDB client initialized with persistence at: {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            self.client = None
    
    def _get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection"""
        if not self.client:
            logger.warning("ChromaDB client not available, returning None")
            return None
            
        try:
            # Try to get existing collection
            collection = self.client.get_collection(collection_name)
            logger.debug(f"Retrieved existing collection: {collection_name}")
            
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def add_resume_embedding(self, resume_id: int, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a resume embedding to the vector store
        
        Args:
            resume_id: Unique identifier for the resume
            text: Resume text content
            metadata: Additional metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        if not CHROMADB_AVAILABLE or not self.client:
            logger.warning("ChromaDB not available, skipping embedding storage")
            return True  # Return True to not break the application flow
            
        try:
            collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            if not collection:
                return True
            
            # Generate embedding
            embedding = self.embedding_service.generate_embedding(text)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                "type": "resume",
                "resume_id": resume_id,
                "text_length": len(text)
            })
            
            # Add to collection
            collection.add(
                embeddings=[embedding.tolist()],
                documents=[text[:1000]],  # Store truncated text for reference
                metadatas=[metadata],
                ids=[f"resume_{resume_id}"]
            )
            
            logger.info(f"Added resume embedding for ID: {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add resume embedding for ID {resume_id}: {e}")
            return False
    
    def add_job_description_embedding(self, jd_id: int, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a job description embedding to the vector store
        
        Args:
            jd_id: Unique identifier for the job description
            text: Job description text content
            metadata: Additional metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            
            # Generate embedding
            embedding = self.embedding_service.generate_embedding(text)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                "type": "job_description",
                "jd_id": jd_id,
                "text_length": len(text)
            })
            
            # Add to collection
            collection.add(
                embeddings=[embedding.tolist()],
                documents=[text[:1000]],  # Store truncated text for reference
                metadatas=[metadata],
                ids=[f"jd_{jd_id}"]
            )
            
            logger.info(f"Added job description embedding for ID: {jd_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job description embedding for ID {jd_id}: {e}")
            return False
    
    def search_similar_resumes(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for resumes similar to the query text
        
        Args:
            query_text: Text to search for
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing resume information and similarity scores
        """
        if not CHROMADB_AVAILABLE or not self.client:
            logger.warning("ChromaDB not available, returning empty search results")
            return []
            
        try:
            collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            if not collection:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query_text)
            
            # Search in collection
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'resume_id': results['metadatas'][0][i].get('resume_id'),
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i],
                        'document_preview': results['documents'][0][i]
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} similar resumes")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar resumes: {e}")
            return []
    
    def search_similar_job_descriptions(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for job descriptions similar to the query text
        
        Args:
            query_text: Text to search for
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing job description information and similarity scores
        """
        try:
            collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query_text)
            
            # Search in collection
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["metadatas", "documents", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'jd_id': results['metadatas'][0][i].get('jd_id'),
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i],
                        'document_preview': results['documents'][0][i]
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} similar job descriptions")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar job descriptions: {e}")
            return []
    
    def calculate_resume_jd_similarity(self, resume_id: int, jd_id: int) -> float:
        """
        Calculate similarity between a specific resume and job description
        
        Args:
            resume_id: Resume identifier
            jd_id: Job description identifier
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            resume_collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            jd_collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            
            # Get resume embedding
            resume_results = resume_collection.get(
                ids=[f"resume_{resume_id}"],
                include=["embeddings"]
            )
            
            # Get job description embedding
            jd_results = jd_collection.get(
                ids=[f"jd_{jd_id}"],
                include=["embeddings"]
            )
            
            if (not resume_results['embeddings'] or not resume_results['embeddings'][0] or
                not jd_results['embeddings'] or not jd_results['embeddings'][0]):
                logger.warning(f"Missing embeddings for resume {resume_id} or JD {jd_id}")
                return 0.0
            
            # Calculate similarity
            resume_embedding = np.array(resume_results['embeddings'][0])
            jd_embedding = np.array(jd_results['embeddings'][0])
            
            similarity = self.embedding_service.calculate_similarity(resume_embedding, jd_embedding)
            
            logger.debug(f"Calculated similarity between resume {resume_id} and JD {jd_id}: {similarity}")
            return similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity between resume {resume_id} and JD {jd_id}: {e}")
            return 0.0
    
    def update_resume_embedding(self, resume_id: int, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Update an existing resume embedding"""
        try:
            collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            
            # Delete existing embedding
            collection.delete(ids=[f"resume_{resume_id}"])
            
            # Add new embedding
            return self.add_resume_embedding(resume_id, text, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update resume embedding for ID {resume_id}: {e}")
            return False
    
    def update_job_description_embedding(self, jd_id: int, text: str, metadata: Dict[str, Any] = None) -> bool:
        """Update an existing job description embedding"""
        try:
            collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            
            # Delete existing embedding
            collection.delete(ids=[f"jd_{jd_id}"])
            
            # Add new embedding
            return self.add_job_description_embedding(jd_id, text, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update job description embedding for ID {jd_id}: {e}")
            return False
    
    def delete_resume_embedding(self, resume_id: int) -> bool:
        """Delete a resume embedding"""
        try:
            collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            collection.delete(ids=[f"resume_{resume_id}"])
            logger.info(f"Deleted resume embedding for ID: {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete resume embedding for ID {resume_id}: {e}")
            return False
    
    def delete_job_description_embedding(self, jd_id: int) -> bool:
        """Delete a job description embedding"""
        try:
            collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            collection.delete(ids=[f"jd_{jd_id}"])
            logger.info(f"Deleted job description embedding for ID: {jd_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job description embedding for ID {jd_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collections"""
        try:
            resume_collection = self._get_or_create_collection(self.RESUME_COLLECTION)
            jd_collection = self._get_or_create_collection(self.JOB_DESCRIPTION_COLLECTION)
            
            resume_count = resume_collection.count()
            jd_count = jd_collection.count()
            
            return {
                "resume_embeddings": resume_count,
                "job_description_embeddings": jd_count,
                "total_embeddings": resume_count + jd_count,
                "embedding_dimension": self.embedding_service.get_embedding_dimension()
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "resume_embeddings": 0,
                "job_description_embeddings": 0,
                "total_embeddings": 0,
                "embedding_dimension": 0
            }

# Global instance for easy access
vector_store = VectorStore()

def get_vector_store() -> VectorStore:
    """Get the global vector store instance"""
    return vector_store