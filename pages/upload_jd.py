import streamlit as st
import os
import sys
from datetime import datetime

# Add parent directory to path to import api_connector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_connector import upload_jd, get_jd_list

# Page configuration
st.set_page_config(
    page_title="Upload Job Descriptions",
    page_icon="📝",
    layout="wide"
)

# Page header
st.title("💼 Job Description Upload")
st.markdown("Upload and manage job descriptions for resume analysis")

# Create necessary directory if it doesn't exist
if not os.path.exists("uploads/job_descriptions"):
    os.makedirs("uploads/job_descriptions")

# Function to save uploaded job description using the new API
def save_jd_api(uploaded_file, company_name, role_title, location):
    """Upload job description using the new standalone API"""
    try:
        # Upload the job description using the API
        result = upload_jd(uploaded_file)
        
        if "error" in result:
            st.error(f"Error uploading job description: {result['error']}")
            return False, 0
        
        if result.get("success"):
            return True, result.get("jd_id")
        else:
            return False, 0
            
    except Exception as e:
        st.error(f"Error uploading job description: {str(e)}")
        return False, 0

# Create two columns for the layout
col1, col2 = st.columns([2, 3])

# Upload form in the first column
with col1:
    st.markdown("### Upload New Job Description")
    
    with st.form("jd_upload_form"):
        company_name = st.text_input("Company Name", placeholder="e.g., Innomatics Research Labs")
        role_title = st.text_input("Job Title", placeholder="e.g., Data Scientist")
        
        # Location selection with common locations for Innomatics
        location = st.selectbox(
            "Location",
            ["Hyderabad", "Bangalore", "Pune", "Delhi NCR", "Remote", "Other"]
        )
        
        uploaded_file = st.file_uploader("Upload Job Description", type=["txt", "pdf", "docx"])
        
        # Key skills extraction
        st.markdown("### Key Skills Required")
        st.text_area("Enter key skills (one per line)", placeholder="Python\nSQL\nMachine Learning\nData Analysis")
        
        submit_button = st.form_submit_button("Upload Job Description")
        
        if submit_button and uploaded_file is not None:
            if company_name and role_title:
                success, jd_id = save_jd_api(uploaded_file, company_name, role_title, location)
                if success:
                    st.success(f"Job description for {role_title} at {company_name} uploaded successfully!")
                    st.info(f"Job Description ID: {jd_id}")
            else:
                st.error("Please fill in all required fields.")

# Display existing job descriptions in the second column
with col2:
    st.markdown("### Existing Job Descriptions")
    
    # Get JD list from API
    try:
        jd_data = get_jd_list()
        
        if jd_data:
            # Display the job descriptions
            st.markdown("#### Job Descriptions")
            for jd in jd_data:
                st.markdown(f"""
                **{jd.get('company', 'Unknown')}** - {jd.get('role', 'Unknown')}  
                📍 {jd.get('location', 'Unknown')} | 📅 {jd.get('upload_date', 'Unknown')}
                """)
                st.divider()
        else:
            st.info("No job descriptions found.")
    except Exception as e:
        st.error(f"Error loading job descriptions: {str(e)}")
        st.info("No job descriptions uploaded yet. Use the form to upload your first job description.")