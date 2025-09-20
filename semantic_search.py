"""
Semantic Search Service for Resume Checker Application

This module provides semantic search functionality using embeddings
to replace the traditional TF-IDF approach for resume-job description matching.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np

from embedding_service import get_embedding_service
from vector_store import get_vector_store
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSearchService:
    """Service for semantic search and analysis using embeddings"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        
    def analyze_resume_semantic(self, resume_text: str, jd_text: str, 
                               resume_id: Optional[int] = None, 
                               jd_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze resume against job description using semantic similarity
        
        Args:
            resume_text: Resume content text
            jd_text: Job description content text
            resume_id: Optional resume ID for embedding storage
            jd_id: Optional job description ID for embedding storage
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Generate embeddings
            resume_embedding = self.embedding_service.generate_embedding(resume_text)
            jd_embedding = self.embedding_service.generate_embedding(jd_text)
            
            # Calculate semantic similarity
            similarity_score = self.embedding_service.calculate_similarity(
                resume_embedding, jd_embedding
            )
            
            # Convert to percentage and determine verdict
            relevance = round(similarity_score * 100, 2)
            verdict = self._determine_verdict(relevance)
            
            # Store embeddings in vector store if IDs provided
            if resume_id:
                self._store_resume_embedding(resume_id, resume_text, resume_embedding)
            if jd_id:
                self._store_jd_embedding(jd_id, jd_text, jd_embedding)
            
            # Extract missing keywords using semantic approach
            missing_keywords = self._extract_semantic_keywords(
                resume_text, jd_text, jd_embedding, resume_embedding
            )
            
            # Generate skills analysis
            technical_skills = self._analyze_technical_skills(resume_text, jd_text)
            soft_skills = self._analyze_soft_skills(resume_text, jd_text)
            
            return {
                "relevance": relevance,
                "verdict": verdict,
                "missing_keywords": missing_keywords[:10],
                "technical_skills": technical_skills,
                "soft_skills": soft_skills,
                "similarity_score": similarity_score,
                "analysis_method": "semantic_embedding"
            }
            
        except Exception as e:
            logger.error(f"Error in semantic analysis: {e}")
            # Fallback to basic analysis
            return self._fallback_analysis(resume_text, jd_text)
    
    def _determine_verdict(self, relevance: float) -> str:
        """Determine verdict based on relevance score"""
        if relevance >= 70:
            return "High"
        elif relevance >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _store_resume_embedding(self, resume_id: int, text: str, embedding: np.ndarray):
        """Store resume embedding in vector store"""
        try:
            # Get resume metadata
            resume_data = self.db.get_resume_by_id(resume_id)
            if not resume_data:
                logger.warning(f"Resume {resume_id} not found in database")
                return
                
            metadata = {
                "resume_id": resume_id,
                "filename": resume_data.get('filename', ''),
                "candidate_name": resume_data.get('candidate_name', ''),
                "job_role": resume_data.get('job_role', ''),
                "email": resume_data.get('email', ''),
                "created_at": datetime.now().isoformat()
            }
            
            self.vector_store.add_resume_embedding(
                resume_id=resume_id,
                text=text,
                embedding=embedding,
                metadata=metadata
            )
            
            # Update database embedding status
            self.db.update_resume_embedding_status(
                resume_id, self.embedding_service.model_name
            )
            
        except Exception as e:
            logger.error(f"Error storing resume embedding: {e}")
    
    def _store_jd_embedding(self, jd_id: int, text: str, embedding: np.ndarray):
        """Store job description embedding in vector store"""
        try:
            # Get JD metadata
            jd_data = self.db.get_job_description_by_id(jd_id)
            if not jd_data:
                logger.warning(f"Job description {jd_id} not found in database")
                return
                
            metadata = {
                "jd_id": jd_id,
                "filename": jd_data.get('filename', ''),
                "company": jd_data.get('company', ''),
                "role": jd_data.get('role', ''),
                "location": jd_data.get('location', ''),
                "created_at": datetime.now().isoformat()
            }
            
            self.vector_store.add_job_description_embedding(
                jd_id=jd_id,
                text=text,
                embedding=embedding,
                metadata=metadata
            )
            
            # Update database embedding status
            self.db.update_job_description_embedding_status(
                jd_id, self.embedding_service.model_name
            )
            
        except Exception as e:
            logger.error(f"Error storing JD embedding: {e}")
    
    def _extract_semantic_keywords(self, resume_text: str, jd_text: str, 
                                 jd_embedding: np.ndarray, 
                                 resume_embedding: np.ndarray) -> List[str]:
        """
        Extract missing keywords using semantic similarity approach
        """
        try:
            # Split JD into sentences/phrases
            jd_sentences = [s.strip() for s in jd_text.split('.') if len(s.strip()) > 10]
            
            missing_concepts = []
            
            # For each JD sentence, check if similar concept exists in resume
            for sentence in jd_sentences[:20]:  # Limit to avoid too many API calls
                sentence_embedding = self.embedding_service.generate_embedding(sentence)
                
                # Calculate similarity with resume
                similarity = self.embedding_service.calculate_similarity(
                    sentence_embedding, resume_embedding
                )
                
                # If similarity is low, this might be a missing concept
                if similarity < 0.3:  # Threshold for missing concepts
                    # Extract key terms from the sentence
                    words = sentence.lower().split()
                    key_words = [w for w in words if len(w) > 3 and w.isalpha()]
                    missing_concepts.extend(key_words[:3])  # Take top 3 words
            
            # Remove duplicates and return
            return list(set(missing_concepts))[:10]
            
        except Exception as e:
            logger.error(f"Error extracting semantic keywords: {e}")
            return []
    
    def _analyze_technical_skills(self, resume_text: str, jd_text: str) -> Dict[str, int]:
        """Analyze technical skills match"""
        # Common technical skills to look for
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue",
            "sql", "mongodb", "postgresql", "mysql", "docker", "kubernetes",
            "aws", "azure", "gcp", "machine learning", "ai", "data science",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"
        ]
        
        skills_analysis = {}
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        for skill in tech_skills:
            if skill in jd_lower:  # Skill is required
                if skill in resume_lower:
                    skills_analysis[skill] = 85  # High match
                else:
                    skills_analysis[skill] = 20  # Missing skill
        
        return skills_analysis
    
    def _analyze_soft_skills(self, resume_text: str, jd_text: str) -> Dict[str, int]:
        """Analyze soft skills match"""
        # Common soft skills to look for
        soft_skills = [
            "communication", "leadership", "teamwork", "problem solving",
            "analytical", "creative", "adaptable", "organized", "detail oriented"
        ]
        
        skills_analysis = {}
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        for skill in soft_skills:
            if skill in jd_lower:  # Skill is required
                if skill in resume_lower:
                    skills_analysis[skill] = 80  # Good match
                else:
                    skills_analysis[skill] = 30  # Potentially missing
        
        return skills_analysis
    
    def _fallback_analysis(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """Fallback analysis in case of errors"""
        return {
            "relevance": 50.0,
            "verdict": "Medium",
            "missing_keywords": [],
            "technical_skills": {},
            "soft_skills": {},
            "similarity_score": 0.5,
            "analysis_method": "fallback"
        }
    
    def search_similar_resumes(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for resumes similar to query text"""
        return self.vector_store.search_similar_resumes(query_text, top_k)
    
    def search_similar_job_descriptions(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for job descriptions similar to query text"""
        return self.vector_store.search_similar_job_descriptions(query_text, top_k)
    
    def get_best_matches(self, resume_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get best job description matches for a resume"""
        try:
            # Get resume data
            resume_data = self.db.get_resume_by_id(resume_id)
            if not resume_data or not resume_data.get('content'):
                return []
            
            # Search for similar job descriptions
            results = self.search_similar_job_descriptions(
                resume_data['content'], top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting best matches for resume {resume_id}: {e}")
            return []

# Global instance
_semantic_search_service = None

def get_semantic_search_service(db_manager: DatabaseManager) -> SemanticSearchService:
    """Get the global semantic search service instance"""
    global _semantic_search_service
    if _semantic_search_service is None:
        _semantic_search_service = SemanticSearchService(db_manager)
    return _semantic_search_service