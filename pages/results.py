import streamlit as st
import sys
import os
import json
import random

# Add the parent directory to the path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Results Dashboard",
    page_icon="📊",
    layout="wide"
)

# Page header
st.title("📊 Results Dashboard")
st.markdown("View analysis results and insights")

# Initialize database
db = DatabaseManager()

# Load data from database
resume_data = db.get_resumes()
jd_data = db.get_job_descriptions()
analysis_results = db.get_analysis_results()

# Check if data exists
if not resume_data:
    st.warning("No resume data available. Please upload resumes first.")
    st.stop()

if not jd_data:
    st.warning("No job description data available. Please upload job descriptions first.")
    st.stop()

# Dashboard metrics
st.markdown("## Dashboard Overview")

# Get statistics from database
stats = db.get_dashboard_stats()

# Create metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Resumes",
        value=stats['total_resumes']
    )

with col2:
    st.metric(
        label="Job Descriptions",
        value=stats['active_job_descriptions']
    )

with col3:
    if analysis_results:
        scores = [float(row['relevance_score']) for row in analysis_results if row['relevance_score']]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    else:
        avg_score = 0
    st.metric(
        label="Average Relevance Score",
        value=f"{avg_score}/100"
    )

with col4:
    high_matches = len([row for row in analysis_results if row['verdict'] == 'High']) if analysis_results else 0
    st.metric(
        label="High Suitability Matches",
        value=high_matches
    )

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Resume Analysis", "Job Role Insights", "Candidate Feedback"])

# Tab 1: Resume Analysis
with tab1:
    st.markdown("### Resume Relevance Analysis")
    
    # Filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Get unique job descriptions for filtering
        jd_names = [jd['filename'] for jd in jd_data] if jd_data else []
        jd_filter = st.multiselect(
            "Filter by Job Description",
            options=jd_names,
            default=[]
        )
    
    with col_filter2:
        verdict_filter = st.multiselect(
            "Filter by Verdict",
            options=["High", "Medium", "Low"],
            default=[]
        )
    
    # Apply filters to analysis results
    filtered_data = analysis_results.copy() if analysis_results else []
    if jd_filter:
        # Filter by job description filename
        jd_ids = [jd['id'] for jd in jd_data if jd['filename'] in jd_filter]
        filtered_data = [row for row in filtered_data if row['job_description_id'] in jd_ids]
    if verdict_filter:
        filtered_data = [row for row in filtered_data if row['verdict'] in verdict_filter]
    
    # Display filtered data
    if filtered_data:
        # Display filtered data as a simple table
        st.markdown("### Resume Analysis Results")
        
        # Create table headers
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
        with col1:
            st.markdown("**Resume**")
        with col2:
            st.markdown("**Job Description**")
        with col3:
            st.markdown("**Analysis Date**")
        with col4:
            st.markdown("**Score**")
        with col5:
            st.markdown("**Verdict**")
        with col6:
            st.markdown("**Details**")
        
        st.markdown("---")
        
        # Create lookup dictionaries for resume and JD data
        resume_lookup = {r['id']: r for r in resume_data}
        jd_lookup = {j['id']: j for j in jd_data}
        
        # Display data rows
        for row in filtered_data:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
            
            # Get resume and JD info
            resume_info = resume_lookup.get(row['resume_id'], {})
            jd_info = jd_lookup.get(row['job_description_id'], {})
            
            with col1:
                st.write(resume_info.get('filename', 'Unknown'))
            with col2:
                st.write(jd_info.get('filename', 'Unknown'))
            with col3:
                st.write(row.get('created_at', 'Unknown'))
            with col4:
                score = float(row['relevance_score']) if row['relevance_score'] else 0
                if score >= 75:
                    st.markdown(f"<span style='color:green'>{score:.1f}</span>", unsafe_allow_html=True)
                elif score >= 50:
                    st.markdown(f"<span style='color:orange'>{score:.1f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:red'>{score:.1f}</span>", unsafe_allow_html=True)
            with col5:
                verdict = row['verdict']
                if verdict == "High":
                    st.markdown(f"<span style='color:green'>{verdict}</span>", unsafe_allow_html=True)
                elif verdict == "Medium":
                    st.markdown(f"<span style='color:orange'>{verdict}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:red'>{verdict}</span>", unsafe_allow_html=True)
            with col6:
                if st.button("View", key=f"view_{row['id']}"):
                    # Show detailed analysis
                    with st.expander("Analysis Details", expanded=True):
                        st.write("**Missing Keywords:**")
                        try:
                            missing_keywords = json.loads(row.get('missing_keywords', '[]'))
                            if missing_keywords:
                                st.write(", ".join(missing_keywords))
                            else:
                                st.write("None")
                        except:
                            st.write("Unable to parse keywords")
                        
                        st.write("**Skills Analysis:**")
                        try:
                            skills_data = json.loads(row.get('skills_data', '{}'))
                            if skills_data:
                                st.json(skills_data)
                            else:
                                st.write("No skills data available")
                        except:
                            st.write("Unable to parse skills data")
        
        # Visualization: Score Distribution
        st.markdown("### Score Distribution")
        
        # Calculate distribution
        scores = [float(row['relevance_score']) for row in filtered_data if row['relevance_score']]
        if scores:
            low_count = len([s for s in scores if s < 50])
            medium_count = len([s for s in scores if 50 <= s < 75])
            high_count = len([s for s in scores if s >= 75])
            
            # Display distribution as metrics
            col_chart1, col_chart2, col_chart3 = st.columns(3)
            with col_chart1:
                st.metric("Low (0-49)", low_count)
            with col_chart2:
                st.metric("Medium (50-74)", medium_count)
            with col_chart3:
                st.metric("High (75-100)", high_count)
        else:
            st.info("No score data available for the selected filters.")
    else:
        st.info("No data available with the selected filters.")

# Tab 2: Job Role Insights
with tab2:
    st.markdown("### Job Role Performance")
    
    if analysis_results:
        # Calculate job role metrics from analysis results
        # First, get job roles from resume data and match with analysis results
        job_roles = list(set([row["job_role"] for row in resume_data]))
        job_metrics = []
        
        for role in job_roles:
            # Get resume IDs for this job role
            role_resume_ids = [row["id"] for row in resume_data if row["job_role"] == role]
            # Get analysis results for these resumes
            role_data = [row for row in analysis_results if row["resume_id"] in role_resume_ids]
            
            if role_data:  # Only process if there are analysis results for this role
                scores = [float(row["relevance_score"]) for row in role_data if row.get("relevance_score")]
                high_count = len([row for row in role_data if row.get("verdict") == "High"])
                
                if scores:  # Only create metrics if there are valid scores
                    metrics = {
                        "job_role": role,
                        "avg_score": round(sum(scores) / len(scores), 1),
                        "min_score": min(scores),
                        "max_score": max(scores),
                        "resume_count": len(role_data),
                        "high_match_percent": round((high_count / len(role_data)) * 100, 1)
                    }
                    job_metrics.append(metrics)
        
        # Display the metrics as a table
        st.markdown("### Job Role Performance Metrics")
        
        # Create table headers
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        with col1:
            st.markdown("**Job Role**")
        with col2:
            st.markdown("**Avg Score**")
        with col3:
            st.markdown("**Min Score**")
        with col4:
            st.markdown("**Max Score**")
        with col5:
            st.markdown("**Count**")
        with col6:
            st.markdown("**High %**")
        
        st.markdown("---")
        
        # Display data rows
        for metrics in job_metrics:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            with col1:
                st.write(metrics["job_role"])
            with col2:
                st.write(metrics["avg_score"])
            with col3:
                st.write(metrics["min_score"])
            with col4:
                st.write(metrics["max_score"])
            with col5:
                st.write(metrics["resume_count"])
            with col6:
                st.write(f"{metrics['high_match_percent']}%")
        
        # Visualization: Average Score by Job Role
        st.markdown("### Average Score by Job Role")
        
        # Sort by average score
        job_metrics_sorted = sorted(job_metrics, key=lambda x: x['avg_score'], reverse=True)
        
        # Display job role metrics as a table
        st.markdown("#### Job Role Performance Summary")
        for metrics in job_metrics_sorted:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{metrics['job_role']}**")
            with col2:
                st.metric("Avg Score", f"{metrics['avg_score']:.1f}")
            with col3:
                st.metric("Candidates", metrics['resume_count'])
    else:
        st.info("No analysis results available for job role insights. Please analyze some resumes first.")

# Tab 3: Candidate Feedback
with tab3:
    st.markdown("### Candidate Feedback and Improvement Suggestions")
    
    # Select a candidate to view feedback
    if resume_data:
        # Create options for selectbox
        candidate_options = []
        for row in resume_data:
            candidate_options.append({
                "filename": row["filename"],
                "display": f"{row['candidate_name']} - {row['job_role']}"
            })
        
        selected_candidate = st.selectbox(
            "Select a candidate",
            options=[opt["filename"] for opt in candidate_options],
            format_func=lambda x: next(opt["display"] for opt in candidate_options if opt["filename"] == x)
        )
        
        if selected_candidate:
            # Get candidate details from resume data
            candidate_info = next(row for row in resume_data if row["filename"] == selected_candidate)
            
            # Get analysis data for this candidate
            candidate_analysis = None
            if analysis_results:
                candidate_analysis = next((row for row in analysis_results if row["resume_id"] == candidate_info["id"]), None)
            
            # Display candidate information
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown(f"**Candidate:** {candidate_info['candidate_name']}")
                st.markdown(f"**Email:** {candidate_info['email']}")
                st.markdown(f"**Job Role:** {candidate_info['job_role']}")
            
            with col_info2:
                if candidate_analysis:
                    st.markdown(f"**Relevance Score:** {candidate_analysis['relevance_score']}/100")
                    
                    # Display verdict with appropriate color
                    if candidate_analysis['verdict'] == "High":
                        st.markdown(f"**Verdict:** <span style='color:green'>{candidate_analysis['verdict']} Suitability</span>", unsafe_allow_html=True)
                    elif candidate_analysis['verdict'] == "Medium":
                        st.markdown(f"**Verdict:** <span style='color:orange'>{candidate_analysis['verdict']} Suitability</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Verdict:** <span style='color:red'>{candidate_analysis['verdict']} Suitability</span>", unsafe_allow_html=True)
                else:
                    st.markdown("**Relevance Score:** Not analyzed yet")
                    st.markdown("**Verdict:** Not analyzed yet")
            
            # Visual Skills Dashboard (VSD)
            st.markdown("### Visual Skills Dashboard (VSD)")
            
            # Get job role requirements from job description data
            job_role = candidate_info['job_role']
            job_requirements = {}
            
            # Check if job role exists in job description data
            job_role_exists = any(row["role"] == job_role for row in jd_data)
            
            if job_role_exists:
                # In a real application, this would extract skills from the job description
                # For now, we'll use predefined skills based on job role
                
                # Common technical skills by role
                tech_skills_by_role = {
                    "Data Scientist": {
                        "Python": 90, 
                        "Data Analysis": 95, 
                        "Machine Learning": 90, 
                        "SQL": 85, 
                        "Statistics": 90
                    },
                    "Software Engineer": {
                        "Java": 85, 
                        "Python": 80, 
                        "JavaScript": 85, 
                        "System Design": 80, 
                        "Cloud Computing": 75
                    },
                    "Product Manager": {
                        "Product Strategy": 90, 
                        "Market Analysis": 85, 
                        "User Research": 80, 
                        "Agile": 75, 
                        "Data Analysis": 70
                    },
                    "UX Designer": {
                        "UI Design": 90, 
                        "User Research": 85, 
                        "Wireframing": 90, 
                        "Prototyping": 85, 
                        "Visual Design": 80
                    }
                }
                
                # Common soft skills by role
                soft_skills_by_role = {
                    "Data Scientist": {
                        "Problem Solving": 90, 
                        "Communication": 80, 
                        "Teamwork": 75, 
                        "Critical Thinking": 85, 
                        "Attention to Detail": 85
                    },
                    "Software Engineer": {
                        "Problem Solving": 90, 
                        "Teamwork": 85, 
                        "Communication": 80, 
                        "Time Management": 75, 
                        "Adaptability": 80
                    },
                    "Product Manager": {
                        "Leadership": 90, 
                        "Communication": 95, 
                        "Strategic Thinking": 90, 
                        "Stakeholder Management": 85, 
                        "Problem Solving": 85
                    },
                    "UX Designer": {
                        "Empathy": 90, 
                        "Communication": 85, 
                        "Collaboration": 85, 
                        "Creativity": 90, 
                        "Attention to Detail": 85
                    }
                }
                
                # Default to Software Engineer if role not found
                default_role = "Software Engineer"
                job_requirements = {
                    "Technical Skills": tech_skills_by_role.get(job_role, tech_skills_by_role[default_role]),
                    "Soft Skills": soft_skills_by_role.get(job_role, soft_skills_by_role[default_role])
                }
            else:
                # Default skills if job role not found
                job_requirements = {
                    "Technical Skills": {
                        "Python": 85,
                        "Data Analysis": 75,
                        "Machine Learning": 60,
                        "SQL": 80,
                        "Cloud Computing": 50
                    },
                    "Soft Skills": {
                        "Communication": 70,
                        "Teamwork": 85,
                        "Problem Solving": 75,
                        "Leadership": 65,
                        "Time Management": 80
                    }
                }
            
            # Generate candidate skills based on relevance score
            # Higher relevance score = closer to job requirements
            if candidate_analysis and candidate_analysis.get('relevance_score'):
                relevance_factor = float(candidate_analysis['relevance_score']) / 100
            else:
                relevance_factor = 0.5  # Default to medium relevance if no analysis available
            
            # Calculate candidate skills by applying a variance to job requirements
            # based on relevance score
            skills_data = {
                "Technical Skills": {},
                "Soft Skills": {}
            }
            
            import random
            
            # Generate candidate technical skills
            for skill, req_value in job_requirements["Technical Skills"].items():
                # Higher relevance means closer to requirements
                # Lower relevance means more variance (potentially lower scores)
                min_variance = -30 * (1 - relevance_factor)  # More negative for lower relevance
                max_variance = 10 * relevance_factor  # More positive for higher relevance
                
                # Apply variance but ensure value is between 0-100
                variance = random.uniform(min_variance, max_variance)
                skill_value = max(0, min(100, req_value + variance))
                skills_data["Technical Skills"][skill] = round(skill_value)
            
            # Generate candidate soft skills
            for skill, req_value in job_requirements["Soft Skills"].items():
                # Soft skills typically have less variance
                min_variance = -20 * (1 - relevance_factor)
                max_variance = 15 * relevance_factor
                
                variance = random.uniform(min_variance, max_variance)
                skill_value = max(0, min(100, req_value + variance))
                skills_data["Soft Skills"][skill] = round(skill_value)
            
            # Create tabs for different skill categories
            vsd_tab1, vsd_tab2 = st.tabs(["Technical Skills", "Soft Skills"])
            
            # Technical Skills Visualization
            with vsd_tab1:
                tech_skills = skills_data["Technical Skills"]
                
                # Display technical skills as a bar chart
                st.markdown("#### Technical Skills Assessment")
                
                # Display technical skills as progress bars
                st.markdown("#### Technical Skills Overview")
                for skill, score in tech_skills.items():
                    st.write(f"**{skill}**: {score}/100")
                    st.progress(score / 100)
                
                # Add skill bars with gap analysis
                st.markdown("#### Technical Skills Breakdown & Gap Analysis")
                
                # Create columns for skill comparison
                for skill, value in tech_skills.items():
                    # Get required skill level from job requirements
                    required_value = job_requirements["Technical Skills"][skill]
                    
                    # Calculate gap
                    gap = required_value - value
                    
                    # Determine color based on value
                    if value >= 75:
                        bar_color = 'green'
                    elif value >= 50:
                        bar_color = 'orange'
                    else:
                        bar_color = 'red'
                    
                    # Create columns for layout
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{skill}**")
                        st.progress(value/100)
                        
                        # Show candidate's value
                        st.markdown(f"<span style='color:{bar_color}'>{value}%</span> (Candidate)", unsafe_allow_html=True)
                        
                        # Show required value with a different style
                        st.markdown(f"<span style='color:blue'>{required_value}%</span> (Required)", unsafe_allow_html=True)
                    
                    with col2:
                        # Display gap analysis
                        if gap <= 0:
                            st.markdown(f"<span style='color:green'>✓ Meets requirement</span>", unsafe_allow_html=True)
                        elif gap <= 10:
                            st.markdown(f"<span style='color:orange'>⚠ Minor gap: {gap}%</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:red'>✗ Significant gap: {gap}%</span>", unsafe_allow_html=True)
                            
                    # Add a separator between skills
                    st.markdown("---")
            
            # Soft Skills Visualization
            with vsd_tab2:
                soft_skills = skills_data["Soft Skills"]
                
                # Display soft skills as a bar chart
                st.markdown("#### Soft Skills Assessment")
                
                # Display soft skills as progress bars
                st.markdown("#### Soft Skills Overview")
                for skill, score in soft_skills.items():
                    st.write(f"**{skill}**: {score}/100")
                    st.progress(score / 100)
                
                # Add skill bars with gap analysis
                st.markdown("#### Soft Skills Breakdown & Gap Analysis")
                
                # Create columns for skill comparison
                for skill, value in soft_skills.items():
                    # Get required skill level from job requirements
                    required_value = job_requirements["Soft Skills"][skill]
                    
                    # Calculate gap
                    gap = required_value - value
                    
                    # Determine color based on value
                    if value >= 75:
                        bar_color = 'green'
                    elif value >= 50:
                        bar_color = 'orange'
                    else:
                        bar_color = 'red'
                    
                    # Create columns for layout
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{skill}**")
                        st.progress(value/100)
                        
                        # Show candidate's value
                        st.markdown(f"<span style='color:{bar_color}'>{value}%</span> (Candidate)", unsafe_allow_html=True)
                        
                        # Show required value with a different style
                        st.markdown(f"<span style='color:blue'>{required_value}%</span> (Required)", unsafe_allow_html=True)
                    
                    with col2:
                        # Display gap analysis
                        if gap <= 0:
                            st.markdown(f"<span style='color:green'>✓ Meets requirement</span>", unsafe_allow_html=True)
                        elif gap <= 10:
                            st.markdown(f"<span style='color:orange'>⚠ Minor gap: {gap}%</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:red'>✗ Significant gap: {gap}%</span>", unsafe_allow_html=True)
                            
                    # Add a separator between skills
                    st.markdown("---")
            
            # Display feedback based on verdict (mock data for demo)
            st.markdown("### Feedback Summary")
            
            if candidate_analysis and candidate_analysis.get('verdict'):
                verdict = candidate_analysis['verdict']
                if verdict == "High":
                    st.success("This candidate is a strong match for the role!")
                    st.markdown("""
                    **Strengths:**
                    - Strong technical skills matching job requirements
                    - Relevant experience in similar roles
                    - Good educational background
                    
                    **Suggestions for Improvement:**
                    - Consider adding more specific project details
                    - Highlight leadership experience if available
                    - Add any relevant certifications
                    """)
                elif verdict == "Medium":
                    st.warning("This candidate has potential but some gaps exist.")
                    st.markdown("""
                    **Strengths:**
                    - Basic technical skills present
                    - Some relevant experience
                    
                    **Areas for Improvement:**
                    - Enhance technical skills in: Advanced Data Visualization, Cloud Computing
                    - Add more specific project examples demonstrating required skills
                    - Consider obtaining relevant certifications
                    - Highlight any team collaboration experiences
                    """)
                else:
                    st.error("This candidate needs significant improvement to match the role.")
                    st.markdown("""
                    **Areas for Improvement:**
                    - Develop core technical skills required for the role
                    - Gain practical experience through projects or internships
                    - Complete relevant courses or certifications
                    - Restructure resume to highlight relevant experiences
                    - Add specific examples of work related to the job requirements
                    """)
            else:
                st.info("No analysis available for this candidate. Please analyze their resume first.")
                st.markdown("""
                **To get feedback:**
                - Upload this candidate's resume for analysis
                - Compare against relevant job descriptions
                - Return here to view detailed feedback and improvement suggestions
                """)
            
            # Action buttons
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Send Feedback to Candidate"):
                    st.info("Feedback would be sent to the candidate's email (demo only).")
            
            with col_btn2:
                if st.button("Download Detailed Report"):
                    st.info("Detailed report would be downloaded (demo only).")
    else:
        st.info("No candidate data available for feedback.")