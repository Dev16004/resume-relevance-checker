import streamlit as st
import os
import csv
from datetime import datetime
import fitz  # PyMuPDF

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

# Function to save uploaded job description
def save_jd(uploaded_file, company_name, role_title, location):
    # Create a timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company_name}_{role_title}_{timestamp}.txt"
    filepath = os.path.join("uploads/job_descriptions", filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Save metadata
    new_row = {
        "filename": filename,
        "company": company_name,
        "role": role_title,
        "location": location,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Active"
    }
    
    # Check if metadata file exists
    file_exists = os.path.exists("uploads/job_descriptions/metadata.csv")
    
    with open("uploads/job_descriptions/metadata.csv", 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["filename", "company", "role", "location", "upload_date", "status"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(new_row)
    
    return True

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
                success = save_jd(uploaded_file, company_name, role_title, location)
                if success:
                    st.success(f"Job description for {role_title} at {company_name} uploaded successfully!")
            else:
                st.error("Please fill in all required fields.")

# Display existing job descriptions in the second column
with col2:
    st.markdown("### Existing Job Descriptions")
    
    # Check if metadata file exists
    if os.path.exists("uploads/job_descriptions/metadata.csv"):
        jd_data = []
        with open("uploads/job_descriptions/metadata.csv", 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                jd_data.append(row)
        
        if jd_data:
            # Get unique values for filters
            companies = list(set(row["company"] for row in jd_data))
            locations = list(set(row["location"] for row in jd_data))
            
            # Add filters
            st.markdown("#### Filter Job Descriptions")
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                company_filter = st.multiselect(
                    "Company",
                    options=companies,
                    default=[]
                )
            
            with col_filter2:
                location_filter = st.multiselect(
                    "Location",
                    options=locations,
                    default=[]
                )
            
            # Apply filters
            filtered_data = jd_data
            if company_filter:
                filtered_data = [row for row in filtered_data if row["company"] in company_filter]
            if location_filter:
                filtered_data = [row for row in filtered_data if row["location"] in location_filter]
        
            # Display the filtered data
            if filtered_data:
                st.markdown("#### Job Descriptions")
                for row in filtered_data:
                    st.markdown(f"""
                    **{row['company']}** - {row['role']}  
                    📍 {row['location']} | 📅 {row['upload_date']} | 🔄 {row['status']}
                    """)
                    st.divider()
                
                # Allow viewing job description details
                jd_options = [row["filename"] for row in filtered_data]
                jd_labels = [f"{row['company']} - {row['role']}" for row in filtered_data]
                
                selected_jd = st.selectbox(
                    "Select a job description to view details",
                    options=jd_options,
                    format_func=lambda x: next(label for i, label in enumerate(jd_labels) if jd_options[i] == x)
                )
            
            if selected_jd:
                jd_path = os.path.join("uploads/job_descriptions", selected_jd)
                if os.path.exists(jd_path):
                    # Extract text from PDF file
                    jd_content = None
                    try:
                        # Open PDF file
                        pdf_document = fitz.open(jd_path)
                        jd_content = ""
                        
                        # Extract text from all pages
                        for page_num in range(pdf_document.page_count):
                            page = pdf_document[page_num]
                            jd_content += page.get_text()
                        
                        pdf_document.close()
                        
                        if not jd_content.strip():
                            jd_content = "No text content found in the PDF file."
                            
                    except Exception as e:
                        st.error(f"Could not read the PDF file {selected_jd}. Error: {str(e)}")
                        jd_content = "Error reading PDF file content."
                    
                    with st.expander("Job Description Content", expanded=True):
                        st.text_area("", value=jd_content, height=300, disabled=True)
                        
                        col_actions1, col_actions2 = st.columns(2)
                        with col_actions1:
                            if st.button("Mark as Inactive", key="inactive_btn"):
                                # Update status in metadata
                                for row in jd_data:
                                    if row["filename"] == selected_jd:
                                        row["status"] = "Inactive"
                                
                                # Write updated data back to CSV
                                with open("uploads/job_descriptions/metadata.csv", 'w', newline='', encoding='utf-8') as csvfile:
                                    if jd_data:
                                        fieldnames = jd_data[0].keys()
                                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                        writer.writeheader()
                                        writer.writerows(jd_data)
                                
                                st.success("Job description marked as inactive!")
                                st.rerun()
                        
                        with col_actions2:
                            if st.button("Delete Job Description", key="delete_btn"):
                                # Remove file and update metadata
                                os.remove(jd_path)
                                jd_data = [row for row in jd_data if row["filename"] != selected_jd]
                                
                                # Write updated data back to CSV
                                with open("uploads/job_descriptions/metadata.csv", 'w', newline='', encoding='utf-8') as csvfile:
                                    if jd_data:
                                        fieldnames = jd_data[0].keys()
                                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                        writer.writeheader()
                                        writer.writerows(jd_data)
                                
                                st.success("Job description deleted successfully!")
                                st.rerun()
            else:
                st.info("No job descriptions match the selected filters.")
        else:
            st.info("No job descriptions found in the metadata file.")
    else:
        st.info("No job descriptions uploaded yet. Use the form to upload your first job description.")