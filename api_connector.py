"""
Standalone API Connector for Streamlit Cloud Deployment

This module provides direct integration of backend functionality
without requiring a separate Flask server, making it suitable for
Streamlit Cloud deployment.
"""

import streamlit as st
import os
import json
import tempfile
import docx2txt
import fitz  # PyMuPDF
from PIL import Image
import io
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import local modules
from database import DatabaseManager
from semantic_search import get_semantic_search_service
from embedding_service import get_embedding_service

class StandaloneAPI:
    """Standalone API that integrates backend functionality directly"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.semantic_search = get_semantic_search_service(self.db)
        self.embedding_service = get_embedding_service()
        
        # Create upload directories if they don't exist
        self.upload_dirs = {
            'resume': 'uploads/resumes',
            'jd': 'uploads/jds'
        }
        for dir_path in self.upload_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def extract_text_from_file(self, file, file_type: str) -> str:
        """Extract text from uploaded file"""
        try:
            if file_type == 'application/pdf':
                # Handle PDF files
                pdf_bytes = file.read()
                pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = ""
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    text += page.get_text()
                pdf_document.close()
                return text
                
            elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                # Handle DOCX files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(file.read())
                    tmp_file.flush()
                    text = docx2txt.process(tmp_file.name)
                os.unlink(tmp_file.name)
                return text
                
            elif file_type == 'text/plain':
                # Handle TXT files
                return file.read().decode('utf-8')
                
            else:
                return "Unsupported file format"
                
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return ""
    
    def upload_resume(self, file, candidate_name: str = "Unknown", email: str = None, job_role: str = "Unknown", phone: str = None) -> Dict[str, Any]:
        """Process resume upload"""
        try:
            # Extract text from file
            text_content = self.extract_text_from_file(file, file.type)
            
            if not text_content:
                return {"error": "Could not extract text from file"}
            
            # Save to database
            resume_id = self.db.save_resume(
                filename=file.name,
                content=text_content,
                file_type=file.type,
                candidate_name=candidate_name,
                email=email,
                job_role=job_role,
                phone=phone
            )
            
            # Save file to uploads directory
            file_path = os.path.join(self.upload_dirs['resume'], f"{resume_id}_{file.name}")
            with open(file_path, 'wb') as f:
                file.seek(0)  # Reset file pointer
                f.write(file.read())
            
            return {
                "success": True,
                "resume_id": resume_id,
                "filename": file.name,
                "text_length": len(text_content),
                "message": "Resume uploaded successfully"
            }
            
        except Exception as e:
            return {"error": f"Error uploading resume: {str(e)}"}
    
    def upload_jd(self, file, company="Unknown", role="Unknown", location="Unknown") -> Dict[str, Any]:
        """Process job description upload"""
        try:
            # Extract text from file
            text_content = self.extract_text_from_file(file, file.type)
            
            if not text_content:
                return {"error": "Could not extract text from file"}
            
            # Save to database
            jd_id = self.db.save_job_description(
                filename=file.name,
                content=text_content,
                file_type=file.type,
                company=company,
                role=role,
                location=location
            )
            
            # Save file to uploads directory
            file_path = os.path.join(self.upload_dirs['jd'], f"{jd_id}_{file.name}")
            with open(file_path, 'wb') as f:
                file.seek(0)  # Reset file pointer
                f.write(file.read())
            
            return {
                "success": True,
                "jd_id": jd_id,
                "filename": file.name,
                "text_length": len(text_content),
                "message": "Job description uploaded successfully"
            }
            
        except Exception as e:
            return {"error": f"Error uploading job description: {str(e)}"}
    
    def analyze_resume_jd(self, resume_id: int, jd_id: int) -> Dict[str, Any]:
        """Analyze resume against job description"""
        try:
            # Get resume and JD from database
            resume_data = self.db.get_resume(resume_id)
            jd_data = self.db.get_job_description(jd_id)
            
            if not resume_data or not jd_data:
                return {"error": "Resume or job description not found"}
            
            # Perform semantic analysis
            analysis_result = self.semantic_search.analyze_resume_semantic(
                resume_text=resume_data['content'],
                jd_text=jd_data['content'],
                resume_id=resume_id,
                jd_id=jd_id
            )
            
            # Save analysis result
            analysis_id = self.db.save_analysis_result(
                resume_id=resume_id,
                jd_id=jd_id,
                analysis_data=analysis_result
            )
            
            analysis_result['analysis_id'] = analysis_id
            return analysis_result
            
        except Exception as e:
            return {"error": f"Error analyzing resume: {str(e)}"}
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history"""
        try:
            return self.db.get_analysis_history()
        except Exception as e:
            return []
    
    def get_resume_list(self) -> List[Dict[str, Any]]:
        """Get list of uploaded resumes"""
        try:
            return self.db.get_resume_list()
        except Exception as e:
            return []
    
    def get_jd_list(self) -> List[Dict[str, Any]]:
        """Get list of uploaded job descriptions"""
        try:
            return self.db.get_jd_list()
        except Exception as e:
            return []

# Global API instance
_api_instance = None

def get_api():
    """Get singleton API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = StandaloneAPI()
    return _api_instance

# Backward compatibility functions
def upload_resume(file, candidate_name: str = "Unknown", email: str = None, job_role: str = "Unknown", phone: str = None):
    """Upload a resume file"""
    api = get_api()
    return api.upload_resume(file, candidate_name, email, job_role, phone)

def upload_jd(file, company="Unknown", role="Unknown", location="Unknown"):
    """Upload a job description file"""
    api = get_api()
    return api.upload_jd(file, company, role, location)

def analyze_resume_jd(resume_id, jd_id):
    """Analyze resume against job description"""
    api = get_api()
    return api.analyze_resume_jd(resume_id, jd_id)

def get_analysis_history():
    """Get analysis history"""
    api = get_api()
    return api.get_analysis_history()

def get_resume_list():
    """Get list of uploaded resumes"""
    api = get_api()
    return api.get_resume_list()

def get_jd_list():
    """Get list of uploaded job descriptions"""
    api = get_api()
    return api.get_jd_list()

def check_backend_health():
    """Check if backend is healthy (always returns True for standalone)"""
    return {"status": "healthy", "message": "Standalone mode active"}

def start_backend_server():
    """Start backend server (no-op for standalone)"""
    return {"status": "running", "message": "Standalone mode - no server needed"}

def is_backend_running():
    """Check if backend is running (always True for standalone mode)"""
    return True

def get_available_models():
    """Get available embedding models"""
    api = get_api()
    return {"models": api.embedding_service.get_available_models()}

def get_current_model():
    """Get current embedding model"""
    api = get_api()
    return {"model": api.embedding_service.get_model_info()}

def switch_model(model_key):
    """Switch to a different embedding model"""
    api = get_api()
    try:
        api.embedding_service.switch_model(model_key)
        return {"status": "success", "message": f"Switched to model: {model_key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}