import streamlit as st
import sys
import os
import json
import random

# Add the parent directory to the path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager
from api_connector import analyze_resume_jd

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

# Analysis Trigger Section
st.markdown("## 🔍 Run Analysis")
if not analysis_results:
    st.info("No analysis results found. Run analysis between resumes and job descriptions to see results.")

with st.expander("Run New Analysis", expanded=not analysis_results):
    col_resume, col_jd, col_button = st.columns([2, 2, 1])
    
    with col_resume:
        # Create resume options
        resume_options = {}
        for resume in resume_data:
            display_name = f"{resume['candidate_name']} - {resume['job_role']}" if resume['candidate_name'] != 'Unknown' else f"Resume {resume['id']} - {resume['job_role']}"
            resume_options[display_name] = resume['id']
        
        selected_resume = st.selectbox(
            "Select Resume",
            options=list(resume_options.keys()),
            key="resume_select"
        )
    
    with col_jd:
        # Create JD options
        jd_options = {}
        for jd in jd_data:
            display_name = f"{jd['company']} - {jd['role']}"
            jd_options[display_name] = jd['id']
        
        selected_jd = st.selectbox(
            "Select Job Description",
            options=list(jd_options.keys()),
            key="jd_select"
        )
    
    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🚀 Run Analysis", type="primary"):
            if selected_resume and selected_jd:
                resume_id = resume_options[selected_resume]
                jd_id = jd_options[selected_jd]
                
                with st.spinner("Running AI-powered analysis..."):
                    try:
                        result = analyze_resume_jd(resume_id, jd_id)
                        if "error" in result:
                            st.error(f"Analysis failed: {result['error']}")
                        else:
                            st.success("Analysis completed successfully!")
                            st.info("Refresh the page to see the updated results.")
                            # Reload data to show new results
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error running analysis: {str(e)}")
            else:
                st.error("Please select both a resume and job description.")

st.markdown("---")

# Dashboard metrics
st.markdown("## Dashboard Overview")

if analysis_results:
    # Calculate metrics
    total_analyses = len(analysis_results)
    avg_score = sum(float(row['relevance_score']) for row in analysis_results if row['relevance_score']) / len(analysis_results) if analysis_results else 0
    high_matches = len([row for row in analysis_results if float(row['relevance_score']) >= 75])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Analyses", total_analyses)
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}%")
    with col3:
        st.metric("High Matches", high_matches)
    with col4:
        st.metric("Success Rate", f"{(high_matches/total_analyses*100):.1f}%" if total_analyses > 0 else "0%")
else:
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
        st.metric(
            label="Average Relevance Score",
            value="0/100"
        )
    
    with col4:
        st.metric(
            label="High Suitability Matches",
            value=0
        )

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 Analysis Results", "📈 Job Role Insights", "🎯 Skills Analysis"])

# Tab 1: Analysis Results
with tab1:
    st.markdown("### Filter Results")
    
    # Filter controls
    col_filter1, col_filter2 = st.columns(2)
    
    # Get unique job description names for filter
    jd_names = list(set([jd['filename'] for jd in jd_data]))
    
    with col_filter1:
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
        # Display detailed analysis results
        st.markdown("### Resume Analysis Results")
        
        # Create lookup dictionaries for resume and JD data
        resume_lookup = {r['id']: r for r in resume_data}
        jd_lookup = {j['id']: j for j in jd_data}
        
        # Display each analysis result in detail
        for idx, row in enumerate(filtered_data):
            # Get resume and JD info
            resume_info = resume_lookup.get(row['resume_id'], {})
            jd_info = jd_lookup.get(row['job_description_id'], {})
            
            # Create a container for each result
            with st.container():
                st.markdown("---")
                
                # Header with resume and JD info
                col_header1, col_header2, col_header3 = st.columns([2, 2, 1])
                with col_header1:
                    st.markdown(f"**Resume:** {resume_info.get('filename', 'Unknown')}")
                    if resume_info.get('candidate_name', 'Unknown') != 'Unknown':
                        st.markdown(f"*Candidate:* {resume_info.get('candidate_name')}")
                with col_header2:
                    st.markdown(f"**Job Description:** {jd_info.get('filename', 'Unknown')}")
                    st.markdown(f"*Company:* {jd_info.get('company', 'Unknown')} - *Role:* {jd_info.get('role', 'Unknown')}")
                with col_header3:
                    score = float(row['relevance_score']) if row['relevance_score'] else 0
                    verdict = row['verdict']
                    
                    # Score display with color coding
                    if score >= 75:
                        st.markdown(f"<h2 style='color:green; text-align:center'>{score:.1f}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:green; text-align:center; font-weight:bold'>{verdict}</p>", unsafe_allow_html=True)
                    elif score >= 50:
                        st.markdown(f"<h2 style='color:orange; text-align:center'>{score:.1f}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:orange; text-align:center; font-weight:bold'>{verdict}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h2 style='color:red; text-align:center'>{score:.1f}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:red; text-align:center; font-weight:bold'>{verdict}</p>", unsafe_allow_html=True)
                
                # Analysis details in columns
                col_analysis1, col_analysis2 = st.columns([1, 1])
                
                with col_analysis1:
                     st.markdown("#### Key Skills Required")
                     try:
                         # Extract key skills from job description content if available
                         jd_content = jd_info.get('content', '')
                         if jd_content:
                             # Simple keyword extraction for demonstration
                             common_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 'Data Analysis', 'Project Management', 'Communication', 'Leadership']
                             found_skills = [skill for skill in common_skills if skill.lower() in jd_content.lower()]
                             if found_skills:
                                 skills_html = ""
                                 for skill in found_skills[:8]:  # Limit to 8 skills
                                     skills_html += f"<span style='background-color:#e8f5e8; color:#2e7d32; padding:4px 8px; margin:2px; border-radius:12px; font-size:12px; display:inline-block'>{skill}</span> "
                                 st.markdown(skills_html, unsafe_allow_html=True)
                             else:
                                 st.markdown("No specific skills identified")
                         else:
                             st.markdown("Job description content not available")
                     except:
                         st.markdown("Unable to extract key skills")
                     
                     st.markdown("#### Missing Skills")
                     try:
                         # Handle both parsed list and JSON string formats
                         missing_keywords_raw = row.get('missing_keywords', [])
                         if isinstance(missing_keywords_raw, str):
                             missing_keywords = json.loads(missing_keywords_raw)
                         else:
                             missing_keywords = missing_keywords_raw or []
                         
                         # Get relevance score for better logic
                         relevance_score = float(row.get('relevance_score', 0))
                         
                         if missing_keywords:
                             # Display missing skills as prominent tags
                             st.markdown(f"""
                             <div style='background-color:#fff3e0; border-left:4px solid #ff9800; padding:15px; margin:10px 0; border-radius:5px'>
                                 <h5 style='color:#e65100; margin:0 0 10px 0'>⚠️ Skills Gap Identified</h5>
                                 <p style='margin:0; color:#bf360c'>The following skills are missing from the resume:</p>
                             </div>
                             """, unsafe_allow_html=True)
                             
                             missing_skills_html = ""
                             for skill in missing_keywords:
                                 missing_skills_html += f"<span style='background-color:#ffebee; color:#c62828; padding:6px 12px; margin:3px; border-radius:15px; font-size:13px; font-weight:bold; display:inline-block; border:2px solid #ffcdd2'>{skill}</span> "
                             st.markdown(missing_skills_html, unsafe_allow_html=True)
                         elif relevance_score >= 70:
                             # High relevance score with no specific missing keywords
                             st.markdown(f"""
                             <div style='background-color:#e8f5e8; border-left:4px solid #4caf50; padding:15px; margin:10px 0; border-radius:5px'>
                                 <h5 style='color:#2e7d32; margin:0 0 10px 0'>✅ Excellent Skills Match</h5>
                                 <p style='margin:0; color:#1b5e20'>No critical skills gaps identified in this resume.</p>
                             </div>
                             """, unsafe_allow_html=True)
                         elif relevance_score >= 40:
                             # Medium relevance score
                             st.markdown(f"""
                             <div style='background-color:#fff3e0; border-left:4px solid #ff9800; padding:15px; margin:10px 0; border-radius:5px'>
                                 <h5 style='color:#e65100; margin:0 0 10px 0'>⚠️ Moderate Skills Gap</h5>
                                 <p style='margin:0; color:#bf360c'>Some skills improvement needed. Relevance score: {relevance_score}%</p>
                             </div>
                             """, unsafe_allow_html=True)
                         else:
                             # Low relevance score
                             st.markdown(f"""
                             <div style='background-color:#ffebee; border-left:4px solid #f44336; padding:15px; margin:10px 0; border-radius:5px'>
                                 <h5 style='color:#c62828; margin:0 0 10px 0'>❌ Significant Skills Gap</h5>
                                 <p style='margin:0; color:#b71c1c'>Major skills improvement needed. Relevance score: {relevance_score}%</p>
                             </div>
                             """, unsafe_allow_html=True)
                     except:
                         st.markdown(f"""
                         <div style='background-color:#ffebee; border-left:4px solid #f44336; padding:15px; margin:10px 0; border-radius:5px'>
                             <h5 style='color:#c62828; margin:0 0 10px 0'>❌ Analysis Error</h5>
                             <p style='margin:0; color:#b71c1c'>Unable to parse missing skills data.</p>
                         </div>
                         """, unsafe_allow_html=True)
                
                with col_analysis2:
                    st.markdown("#### Skills Analysis")
                    try:
                        # Handle both parsed dict and JSON string formats
                        technical_skills_raw = row.get('technical_skills', {})
                        if isinstance(technical_skills_raw, str):
                            technical_skills = json.loads(technical_skills_raw)
                        else:
                            technical_skills = technical_skills_raw or {}
                            
                        soft_skills_raw = row.get('soft_skills', {})
                        if isinstance(soft_skills_raw, str):
                            soft_skills = json.loads(soft_skills_raw)
                        else:
                            soft_skills = soft_skills_raw or {}
                        
                        if technical_skills or soft_skills:
                            if technical_skills:
                                st.markdown("**Technical Skills Match:**")
                                for skill, score in list(technical_skills.items())[:5]:  # Limit to 5 skills
                                    progress_color = "green" if score >= 75 else "orange" if score >= 50 else "red"
                                    st.markdown(f"• {skill}")
                                    st.progress(score/100)
                            
                            if soft_skills:
                                st.markdown("**Soft Skills Match:**")
                                for skill, score in list(soft_skills.items())[:5]:  # Limit to 5 skills
                                    progress_color = "green" if score >= 75 else "orange" if score >= 50 else "red"
                                    st.markdown(f"• {skill}")
                                    st.progress(score/100)
                        else:
                            st.markdown("No detailed skills analysis available")
                    except Exception as e:
                        st.markdown("Unable to parse skills analysis data")
                    
                    # Analysis date
                    st.markdown("#### Analysis Details")
                    st.markdown(f"**Date:** {row.get('created_at', 'Unknown')}")
                    st.markdown(f"**Analysis ID:** {row.get('id', 'Unknown')}")
        
        # Visualization: Score Distribution
        st.markdown("---")
        st.markdown("### Score Distribution")
        
        # Calculate distribution
        scores = [float(row['relevance_score']) for row in filtered_data if row['relevance_score']]
        if scores:
            low_count = len([s for s in scores if 0 <= s <= 49])  # Low: 0-49
            medium_count = len([s for s in scores if 50 <= s <= 74])  # Medium: 50-74
            high_count = len([s for s in scores if 75 <= s <= 100])  # High: 75-100
            
            # Display distribution as metrics with better styling
            col_chart1, col_chart2, col_chart3 = st.columns(3)
            with col_chart1:
                st.markdown(f"""
                <div style='text-align:center; padding:20px; background-color:#ffebee; border-radius:10px; margin:10px'>
                    <h2 style='color:#c62828; margin:0'>🔴 {low_count}</h2>
                    <p style='color:#c62828; margin:0'>Low (0-49)</p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart2:
                st.markdown(f"""
                <div style='text-align:center; padding:20px; background-color:#fff3e0; border-radius:10px; margin:10px'>
                    <h2 style='color:#f57c00; margin:0'>🟠 {medium_count}</h2>
                    <p style='color:#f57c00; margin:0'>Medium (50-74)</p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart3:
                st.markdown(f"""
                <div style='text-align:center; padding:20px; background-color:#e8f5e8; border-radius:10px; margin:10px'>
                    <h2 style='color:#2e7d32; margin:0'>🟢 {high_count}</h2>
                    <p style='color:#2e7d32; margin:0'>High (75-100)</p>
                </div>
                """, unsafe_allow_html=True)
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

# Tab 3: Skills Analysis
with tab3:
    st.markdown("### Skills Analysis Dashboard")
    
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