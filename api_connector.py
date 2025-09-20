import requests
import os
import json
import streamlit as st
import threading
import time

# API endpoint configuration
API_BASE_URL = "http://localhost:5000/api"

def upload_resume(file):
    """Upload a resume file to the backend API"""
    try:
        files = {'file': (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload/resume", files=files)
        return response.json()
    except Exception as e:
        st.error(f"Error uploading resume: {str(e)}")
        return {"error": str(e)}

def upload_jd(file):
    """Upload a job description file to the backend API"""
    try:
        files = {'file': (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload/jd", files=files)
        return response.json()
    except Exception as e:
        st.error(f"Error uploading job description: {str(e)}")
        return {"error": str(e)}

def analyze_resume(resume_filename, jd_filename):
    """Send a request to analyze a resume against a job description"""
    try:
        data = {
            "resume_filename": resume_filename,
            "jd_filename": jd_filename
        }
        response = requests.post(f"{API_BASE_URL}/analyze", json=data)
        return response.json()
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return {"error": str(e)}

def get_resume_list():
    """Get a list of all uploaded resumes"""
    try:
        response = requests.get(f"{API_BASE_URL}/files/resumes")
        return response.json().get("resumes", [])
    except Exception as e:
        st.error(f"Error getting resume list: {str(e)}")
        return []
        
def upload_omr(file):
    """Upload an OMR sheet image to the backend API for processing"""
    try:
        files = {'file': (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload/omr", files=files)
        return response.json()
    except Exception as e:
        st.error(f"Error uploading OMR sheet: {str(e)}")
        return {"error": str(e)}
        
def evaluate_omr(filename, answer_key):
    """Send a request to evaluate an OMR sheet against an answer key"""
    try:
        data = {
            "filename": filename,
            "answer_key": answer_key
        }
        response = requests.post(f"{API_BASE_URL}/evaluate/omr", json=data)
        return response.json()
    except Exception as e:
        st.error(f"Error evaluating OMR sheet: {str(e)}")
        return {"error": str(e)}

def get_jd_list():
    """Get a list of all uploaded job descriptions"""
    try:
        response = requests.get(f"{API_BASE_URL}/files/jds")
        return response.json().get("job_descriptions", [])
    except Exception as e:
        st.error(f"Error getting job description list: {str(e)}")
        return []

def get_analysis_results():
    """Get a list of all analysis results"""
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/results")
        return response.json().get("analysis_results", [])
    except Exception as e:
        st.error(f"Error getting analysis results: {str(e)}")
        return []

def get_stats():
    """Get application statistics from the database"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        return response.json()
    except Exception as e:
        st.error(f"Error getting statistics: {str(e)}")
        return {}

def is_backend_running():
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/files/resumes", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend_server():
    """Function to start the backend server if it's not running"""
    import subprocess
    import sys
    import threading
    
    def run_server():
        subprocess.run([sys.executable, "backend.py"], 
                      cwd=os.path.dirname(os.path.abspath(__file__)))
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # This ensures the thread will exit when the main program exits
    server_thread.start()
    
    # Wait for server to start
    import time
    for _ in range(5):  # Try 5 times with 1-second intervals
        if is_backend_running():
            return True
        time.sleep(1)
    
    return False

def get_available_models():
    """Get all available embedding models"""
    try:
        response = requests.get(f"{API_BASE_URL}/models/available")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error getting available models: {str(e)}")
        return None

def get_current_model():
    """Get current embedding model information"""
    try:
        response = requests.get(f"{API_BASE_URL}/models/current")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error getting current model: {str(e)}")
        return None

def switch_model(model_key):
    """Switch to a different embedding model"""
    try:
        data = {"model_key": model_key}
        response = requests.post(f"{API_BASE_URL}/models/switch", json=data)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error switching model: {str(e)}")
        return None