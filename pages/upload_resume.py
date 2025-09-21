import streamlit as st
import os
import sys
from datetime import datetime

# Add parent directory to path to import api_connector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_connector import upload_resume

# Page configuration
st.set_page_config(
    page_title="Upload Resumes",
    page_icon="📄",
    layout="wide"
)

# Page header
st.title("📄 Resume Upload")
st.markdown("Upload candidate resumes for analysis and matching")

# Create necessary directory if it doesn't exist
if not os.path.exists("uploads/resumes"):
    os.makedirs("uploads/resumes")

# Function to save uploaded resume using the new API
def save_resume_api(uploaded_file, candidate_name, email, job_role):
    """Upload resume using the new standalone API"""
    try:
        # Upload the resume using the API
        result = upload_resume(uploaded_file)
        
        if "error" in result:
            st.error(f"Error uploading resume: {result['error']}")
            return False, 0, "Error"
        
        if result.get("success"):
            # For now, return basic success info
            # In a full implementation, you might want to store additional metadata
            return True, result.get("resume_id"), "Uploaded"
        else:
            return False, 0, "Failed"
            
    except Exception as e:
        st.error(f"Error uploading resume: {str(e)}")
        return False, 0, "Error"

# Get available job roles from job descriptions using API
def get_available_jobs():
    """Get list of available job roles from uploaded job descriptions"""
    try:
        from api_connector import get_jd_list
        jd_data = get_jd_list()
        if jd_data:
            job_roles = set()
            for jd in jd_data:
                role = jd.get('role', jd.get('title', 'Unknown'))
                if role and role != 'Unknown':
                    job_roles.add(role)
            return list(job_roles) if job_roles else ["No active job roles available"]
        else:
            return ["No active job roles available"]
    except Exception as e:
        return ["No active job roles available"]

# Create two columns for the layout
col1, col2 = st.columns([2, 3])

# Upload form in the first column
with col1:
    st.markdown("### Upload Resume")
    
    with st.form("resume_upload_form"):
        candidate_name = st.text_input("Candidate Name", placeholder="e.g., John Doe")
        email = st.text_input("Email Address", placeholder="e.g., john.doe@example.com")
        
        # Job role selection from available jobs
        available_jobs = get_available_jobs()
        job_role = st.selectbox(
            "Job Role",
            options=available_jobs
        )
        
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        
        submit_button = st.form_submit_button("Upload & Analyze Resume")
        
        if submit_button and uploaded_file is not None:
            if candidate_name and email and job_role != "No active job roles available":
                success, resume_id, status = save_resume_api(uploaded_file, candidate_name, email, job_role)
                if success:
                    st.success(f"Resume for {candidate_name} uploaded successfully!")
                    st.info(f"Resume ID: {resume_id}")
                    st.markdown("You can now upload a job description and run analysis in the Results page.")
            else:
                if job_role == "No active job roles available":
                    st.error("No active job roles available. Please add job descriptions first.")
                else:
                    st.error("Please fill in all required fields.")

# Display existing resumes in the second column
with col2:
    st.markdown("### Uploaded Resumes")
    
    # Get resume list from API
    from api_connector import get_resume_list
    try:
        resume_data = get_resume_list()
        
        if resume_data:
            # Display the data in a simple table format
            st.markdown("#### Resume List")
            for i, resume in enumerate(resume_data):
                st.markdown(f"""
                **Resume ID: {resume.get('id', 'N/A')}** - {resume.get('filename', 'Unknown')}  
                📅 {resume.get('upload_date', 'N/A')} | 📄 {resume.get('file_type', 'N/A')}
                """, unsafe_allow_html=True)
                st.divider()
        else:
            st.info("No resumes uploaded yet.")
    except Exception as e:
        st.error(f"Error loading resumes: {str(e)}")
        st.info("No resumes uploaded yet. Use the form to upload your first resume.")