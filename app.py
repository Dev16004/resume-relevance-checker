"""
AI-Powered Resume Checker - Main Application

This is the main Streamlit application that provides a web interface for the
AI-powered resume checking system. It allows users to upload job descriptions
and resumes, analyze them using AI/ML models, and view comprehensive results.

Features:
- Multi-page web interface using Streamlit
- Backend server management and health checks
- Embedding model configuration and switching
- Integration with Flask backend API
- Real-time analysis and feedback

Author: AI Resume Checker Team
Version: 1.0.0
"""

import streamlit as st
import os
import api_connector

# Set page configuration for the Streamlit app
st.set_page_config(
    page_title="Resume Relevance Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create necessary directories if they don't exist
# These directories store uploaded files and processed data
if not os.path.exists("uploads/resumes"):
    os.makedirs("uploads/resumes")
if not os.path.exists("uploads/job_descriptions"):
    os.makedirs("uploads/job_descriptions")

# Backend server health check and startup
# Ensures the Flask backend is running before the frontend loads
if not api_connector.is_backend_running():
    with st.spinner("Starting backend server..."):
        if api_connector.start_backend_server():
            st.success("Backend server started successfully!")
        else:
            st.error("Failed to start backend server. Some features may not work correctly.")

# Sidebar configuration panel
# Provides model selection and configuration options
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get available embedding models from the backend
    try:
        models_response = api_connector.get_available_models()
        current_model_response = api_connector.get_current_model()
        
        if models_response and current_model_response:
            models = models_response.get('models', {})
            current_model = current_model_response.get('model', {})
            
            # Display current model information
            st.subheader("Embedding Model")
            st.write(f"**Current:** {current_model.get('model_key', 'Unknown')}")
            st.write(f"**Quality:** {current_model.get('quality', 'Unknown')}")
            st.write(f"**Performance:** {current_model.get('performance', 'Unknown')}")
            
            # Model selection dropdown
            # Allows users to switch between different embedding models
            model_options = {}
            for key, config in models.items():
                label = f"{key.title()} - {config['quality']} Quality, {config['performance']} Speed"
                model_options[label] = key
            
            selected_model_label = st.selectbox(
                "Select Embedding Model:",
                options=list(model_options.keys()),
                index=list(model_options.values()).index(current_model.get('model_key', 'fast'))
            )
            
            selected_model_key = model_options[selected_model_label]
            
            # Model switching functionality
            if st.button("Switch Model"):
                with st.spinner("Switching model..."):
                    switch_response = api_connector.switch_model(selected_model_key)
                    if switch_response:
                        st.success(f"Successfully switched to {selected_model_key} model!")
                        st.rerun()
                    else:
                        st.error("Failed to switch model")
            
            # Model info expander
            # Expandable section with detailed model information
            with st.expander("Model Details"):
                for key, config in models.items():
                    st.write(f"**{key.title()}:**")
                    st.write(f"- {config['description']}")
                    st.write(f"- Dimensions: {config['dimensions']}")
                    st.write(f"- Quality: {config['quality']}")
                    st.write(f"- Performance: {config['performance']}")
                    st.write("")
        else:
            st.warning("Could not load model information")
    except Exception as e:
        st.error(f"Error loading model configuration: {e}")

# Main application header and description
st.title("Automated Resume Relevance Check System")
st.subheader("Innomatics Research Labs")

# Application overview and instructions
st.markdown("""
**Welcome to the AI-Powered Resume Checker!**

This system helps you:
- Automatically evaluate resumes against job requirements
- Generate relevance scores for each resume
- Identify skill gaps and missing qualifications
- Provide actionable feedback to candidates

**How to use:**
1. Upload job descriptions in the **Job Description Upload** page
2. Upload candidate resumes in the **Resume Upload** page
3. View matching results and analytics in the **Results Dashboard**

Navigate using the sidebar to access different features.
""")

# System status and information
with st.expander("ℹ️ System Information"):
    st.markdown("""
    **Technology Stack:**
    - Frontend: Streamlit
    - Backend: Flask API
    - Database: SQLite
    - AI/ML: spaCy, NLTK, scikit-learn
    - Vector Search: ChromaDB
    
    **Supported File Formats:**
    - Resumes: PDF, DOCX, TXT
    - Job Descriptions: Text input, PDF, DOCX
    
    **Key Features:**
    - Semantic text analysis
    - Skills gap identification
    - Relevance scoring
    - Candidate ranking
    - Interactive dashboards
    """)

# Application footer with branding and contact information
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <h4>Automated Resume Relevance Check System</h4>
        <p>Developed for Innomatics Research Labs to streamline 
        the resume evaluation process across Hyderabad, 
        Bangalore, Pune, and Delhi NCR.</p>
    </div>
""", unsafe_allow_html=True)