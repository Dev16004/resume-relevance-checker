import streamlit as st
import os
import csv
from datetime import datetime
import random  # For demo purposes to generate random scores

# Page configuration
st.set_page_config(
    page_title="Upload Resumes",
    page_icon="📄",
    layout="wide"
)

# Page header
st.title("Resume Upload")
st.subheader("Upload and analyze candidate resumes")

# Create necessary directory if it doesn't exist
if not os.path.exists("uploads/resumes"):
    os.makedirs("uploads/resumes")

# Function to save uploaded resume
def save_resume(uploaded_file, candidate_name, email, job_role):
    # Create a timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{candidate_name}_{timestamp}.pdf"
    filepath = os.path.join("uploads/resumes", filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Save metadata
    metadata_file = "uploads/resumes/metadata.csv"
    
    # For demo purposes, generate a random relevance score
    relevance_score = random.randint(30, 95)
    
    # Determine verdict based on score
    if relevance_score >= 75:
        verdict = "High"
    elif relevance_score >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"
    
    # Add new row
    new_row = [
        filename,
        candidate_name,
        email,
        job_role,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Pending Review",
        relevance_score,
        verdict
    ]
    
    # Write to CSV
    file_exists = os.path.exists(metadata_file)
    with open(metadata_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Write header if file doesn't exist
            writer.writerow(["filename", "candidate_name", "email", "job_role", "upload_date", "status", "relevance_score", "verdict"])
        writer.writerow(new_row)
    
    return True, relevance_score, verdict

# Get available job roles from job descriptions metadata
def get_available_jobs():
    """Get list of available job roles from uploaded job descriptions"""
    jd_metadata_path = "uploads/job_descriptions/metadata.csv"
    if os.path.exists(jd_metadata_path):
        job_roles = set()
        with open(jd_metadata_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                job_roles.add(row["role"])
        return list(job_roles) if job_roles else ["No active job roles available"]
    else:
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
                success, score, verdict = save_resume(uploaded_file, candidate_name, email, job_role)
                if success:
                    st.success(f"Resume for {candidate_name} uploaded successfully!")
                    
                    # Display the analysis result
                    st.markdown("### Quick Analysis Result")
                    st.markdown(f"**Relevance Score:** {score}/100")
                    
                    # Display verdict with appropriate color
                    if verdict == "High":
                        st.markdown(f"**Verdict:** <span style='color:green'>{verdict} Suitability</span>", unsafe_allow_html=True)
                    elif verdict == "Medium":
                        st.markdown(f"**Verdict:** <span style='color:orange'>{verdict} Suitability</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Verdict:** <span style='color:red'>{verdict} Suitability</span>", unsafe_allow_html=True)
                    
                    st.markdown("View detailed analysis in the Results page.")
            else:
                if job_role == "No active job roles available":
                    st.error("No active job roles available. Please add job descriptions first.")
                else:
                    st.error("Please fill in all required fields.")

# Display existing resumes in the second column
with col2:
    st.markdown("### Uploaded Resumes")
    
    # Display uploaded resumes
    if os.path.exists("uploads/resumes/metadata.csv"):
        # Read CSV data
        resume_data = []
        with open("uploads/resumes/metadata.csv", 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                resume_data.append(row)
        
        if resume_data:
            # Get unique values for filters
            job_roles = list(set(row["job_role"] for row in resume_data))
            
            # Filter section
            st.markdown("#### Filter Resumes")
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                job_filter = st.multiselect(
                    "Job Role",
                    options=job_roles,
                    default=[]
                )
            
            with col_filter2:
                verdict_filter = st.multiselect(
                    "Verdict",
                    options=["High", "Medium", "Low"],
                    default=[]
                )
            
            # Apply filters
            filtered_data = resume_data
            if job_filter:
                filtered_data = [row for row in filtered_data if row["job_role"] in job_filter]
            if verdict_filter:
                filtered_data = [row for row in filtered_data if row["verdict"] in verdict_filter]
            
            # Display filtered data
            if filtered_data:
                # Display the data in a simple table format
                st.markdown("#### Resume List")
                for i, row in enumerate(filtered_data):
                    score = int(row["relevance_score"])
                    if score >= 85:
                        score_color = "green"
                    elif score >= 70:
                        score_color = "orange"
                    else:
                        score_color = "red"
                    
                    st.markdown(f"""
                    **{row['candidate_name']}** - {row['job_role']}  
                    📅 {row['upload_date']} | 📊 <span style='color:{score_color}'>{score}/100</span> | 🎯 {row['verdict']}
                    """, unsafe_allow_html=True)
                    st.divider()
            
            # Allow viewing resume details
            resume_options = [row["filename"] for row in filtered_data]
            resume_labels = [f"{row['candidate_name']} - {row['job_role']}" for row in filtered_data]
            
            selected_resume = st.selectbox(
                "Select a resume to view details",
                options=resume_options,
                format_func=lambda x: next(label for i, label in enumerate(resume_labels) if resume_options[i] == x)
            )
            
            if selected_resume:
                resume_path = os.path.join("uploads/resumes", selected_resume)
                if os.path.exists(resume_path):
                    # Get resume details
                    resume_info = next(row for row in filtered_data if row["filename"] == selected_resume)
                    
                    with st.expander("Resume Details", expanded=True):
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.markdown(f"**Candidate:** {resume_info['candidate_name']}")
                            st.markdown(f"**Email:** {resume_info['email']}")
                            st.markdown(f"**Job Role:** {resume_info['job_role']}")
                        
                        with col_info2:
                            st.markdown(f"**Upload Date:** {resume_info['upload_date']}")
                            st.markdown(f"**Relevance Score:** {resume_info['relevance_score']}/100")
                            
                            # Display verdict with appropriate color
                            if resume_info['verdict'] == "High":
                                st.markdown(f"**Verdict:** <span style='color:green'>{resume_info['verdict']} Suitability</span>", unsafe_allow_html=True)
                            elif resume_info['verdict'] == "Medium":
                                st.markdown(f"**Verdict:** <span style='color:orange'>{resume_info['verdict']} Suitability</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**Verdict:** <span style='color:red'>{resume_info['verdict']} Suitability</span>", unsafe_allow_html=True)
                        
                        # Mock missing skills (for demo purposes)
                        st.markdown("### Missing Skills")
                        if resume_info['verdict'] == "High":
                            st.info("No critical skills missing. Candidate has a strong match for this role.")
                        elif resume_info['verdict'] == "Medium":
                            st.warning("Some skills could be improved:")
                            st.markdown("- Advanced Data Visualization")
                            st.markdown("- Cloud Computing (AWS/Azure)")
                            st.markdown("- Experience with Big Data technologies")
                        else:
                            st.error("Critical skills missing:")
                            st.markdown("- Python Programming")
                            st.markdown("- SQL Database Knowledge")
                            st.markdown("- Machine Learning Fundamentals")
                            st.markdown("- Data Analysis Experience")
                        
                        # Actions
                        col_actions1, col_actions2 = st.columns(2)
                        with col_actions1:
                            if st.button("Mark as Reviewed", key="review_btn"):
                                # Update status in metadata
                                for row in resume_data:
                                    if row["filename"] == selected_resume:
                                        row["status"] = "Reviewed"
                                
                                # Write updated data back to CSV
                                with open("uploads/resumes/metadata.csv", 'w', newline='', encoding='utf-8') as csvfile:
                                    if resume_data:
                                        fieldnames = resume_data[0].keys()
                                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                        writer.writeheader()
                                        writer.writerows(resume_data)
                                
                                st.success("Resume marked as reviewed!")
                                st.rerun()
                        
                        with col_actions2:
                            if st.button("Delete Resume", key="delete_resume_btn"):
                                # Remove file and update metadata
                                os.remove(resume_path)
                                resume_data = [row for row in resume_data if row["filename"] != selected_resume]
                                
                                # Write updated data back to CSV
                                with open("uploads/resumes/metadata.csv", 'w', newline='', encoding='utf-8') as csvfile:
                                    if resume_data:
                                        fieldnames = resume_data[0].keys()
                                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                        writer.writeheader()
                                        writer.writerows(resume_data)
                                
                                st.success("Resume deleted successfully!")
                                st.rerun()
        else:
            st.info("No resumes match the selected filters.")
    else:
        st.info("No resumes uploaded yet. Use the form to upload your first resume.")