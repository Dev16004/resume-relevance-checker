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

# Custom CSS for dark theme and better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0E1117 0%, #262730 50%, #0E1117 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #00D4AA;
    }
    
    .feature-card {
        background: #262730;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #00D4AA;
        margin: 1rem 0;
    }
    
    .tech-stack {
        background: #1E1E1E;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #00D4AA;
        box-shadow: 0 0 10px #00D4AA;
    }
    
    .status-offline {
        background-color: #FF4B4B;
        box-shadow: 0 0 10px #FF4B4B;
    }
    
    .code-block {
        background: #1E1E1E;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        color: #00D4AA;
    }
</style>
""", unsafe_allow_html=True)



# Create necessary directories if they don't exist
# These directories store uploaded files and processed data
if not os.path.exists("uploads/resumes"):
    os.makedirs("uploads/resumes")
if not os.path.exists("uploads/job_descriptions"):
    os.makedirs("uploads/job_descriptions")

# Backend server health check and startup
# Ensures the Flask backend is running before the frontend loads
backend_status = api_connector.is_backend_running()

if not backend_status:
    with st.spinner("🚀 Starting backend server..."):
        if api_connector.start_backend_server():
            st.success("✅ Backend server started successfully!")
            backend_status = True
        else:
            st.error("❌ Failed to start backend server. Some features may not work correctly.")

# Sidebar configuration panel
with st.sidebar:
    st.markdown("### ⚙️ System Configuration")
    
    # Backend status indicator
    status_class = "status-online" if backend_status else "status-offline"
    status_text = "ONLINE" if backend_status else "OFFLINE"
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <span class="status-indicator {status_class}"></span>
        <strong>Backend Status: {status_text}</strong>
    </div>
    """, unsafe_allow_html=True)
    
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

# Main title and description
st.title("📄 Resume Relevance Checker")
st.subheader("Intelligent AI-powered resume analysis and job matching system")

# Welcome message
st.markdown("""
Welcome to the Resume Relevance Checker! This application helps you analyze resumes against job descriptions 
using advanced AI and machine learning techniques.

### How to use:
1. **Upload Job Descriptions** - Navigate to the Job Description Upload page
2. **Upload Resumes** - Add candidate resumes in the Resume Upload section  
3. **View Results** - Check the Results Dashboard for analysis and insights
4. **OMR Evaluation** - Process OMR answer sheets for assessments

Use the sidebar navigation to access all features.
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

# Main content with dark theme styling
st.markdown("""
<div class="main-header">
    <h1 style="color: #00D4AA; text-align: center; margin: 0;">
        📄 Resume Relevance Checker
    </h1>
    <p style="text-align: center; color: #FAFAFA; margin: 0.5rem 0 0 0;">
        Intelligent AI-powered resume analysis and job matching system
    </p>
</div>
""", unsafe_allow_html=True)

# Feature overview cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00D4AA;">🎯 Smart Analysis</h3>
        <p>Advanced AI algorithms analyze resumes and job descriptions for semantic matching and relevance scoring.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00D4AA;">📊 Real-time Results</h3>
        <p>Get instant feedback with detailed analytics, skills gap analysis, and candidate ranking.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00D4AA;">🔍 Vector Search</h3>
        <p>Powered by ChromaDB for efficient semantic search and similarity matching.</p>
    </div>
    """, unsafe_allow_html=True)

# How to use section
st.markdown("### 🚀 Getting Started")

steps = [
    ("📝 Upload Job Descriptions", "Navigate to the Job Description Upload page"),
    ("📄 Upload Resumes", "Add candidate resumes in the Resume Upload section"),
    ("📊 View Results", "Check the Results Dashboard for analysis and insights"),
    ("⚙️ Configure Models", "Use the sidebar to switch between AI models")
]

for i, (title, description) in enumerate(steps, 1):
    st.markdown(f"""
    <div class="code-block">
        <strong>{i}. {title}</strong><br>
        {description}
    </div>
    """, unsafe_allow_html=True)

# Technology stack and features
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="tech-stack">
        <h4 style="color: #00D4AA;">🛠️ Technology Stack</h4>
        <ul style="color: #FAFAFA;">
            <li><strong>Frontend:</strong> Streamlit</li>
            <li><strong>Backend:</strong> Flask API</li>
            <li><strong>Database:</strong> SQLite</li>
            <li><strong>AI/ML:</strong> spaCy, NLTK, scikit-learn</li>
            <li><strong>Vector Search:</strong> ChromaDB</li>
            <li><strong>Embeddings:</strong> Sentence Transformers</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tech-stack">
        <h4 style="color: #00D4AA;">📁 Supported Formats</h4>
        <ul style="color: #FAFAFA;">
            <li><strong>Resumes:</strong> PDF, DOCX, TXT</li>
            <li><strong>Job Descriptions:</strong> Text input, PDF, DOCX</li>
        </ul>
        
        <h4 style="color: #00D4AA; margin-top: 1rem;">✨ Key Features</h4>
        <ul style="color: #FAFAFA;">
            <li>Semantic text analysis</li>
            <li>Skills gap identification</li>
            <li>Relevance scoring</li>
            <li>Candidate ranking</li>
            <li>Interactive dashboards</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p><strong>🤖 Automated Resume Relevance Check System</strong></p>
    <p>Powered by AI • Built with ❤️ • Ready for Production</p>
</div>
""", unsafe_allow_html=True)