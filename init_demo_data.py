#!/usr/bin/env python3
"""
Demo Data Initialization Script for Resume Checker

This script initializes the database with sample data for demonstration purposes.
It's designed to run automatically on deployment to showcase the application's capabilities.

Author: Resume Checker Team
Version: 1.0.0
"""

import os
import sys
from database import DatabaseManager
from semantic_search import SemanticSearchService

def init_demo_data():
    """Initialize database with demo data for deployment"""
    
    print("🚀 Initializing demo data for Resume Checker...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Check if data already exists
    existing_resumes = db.get_resumes()
    existing_jds = db.get_job_descriptions()
    existing_results = db.get_analysis_results()
    
    if existing_resumes and existing_jds and existing_results:
        print("✅ Demo data already exists. Skipping initialization.")
        return
    
    # Sample Job Description
    sample_jd = {
        'filename': 'Data_Engineer_Position.txt',
        'company': 'TechCorp Solutions',
        'role': 'Senior Data Engineer',
        'location': 'San Francisco, CA',
        'content': '''
We are seeking a highly skilled Senior Data Engineer to join our growing data team. 

Key Responsibilities:
- Design and implement scalable data pipelines using Python and SQL
- Work with cloud platforms (AWS, Azure) for data processing
- Collaborate with data scientists and analysts to deliver insights
- Optimize database performance and ensure data quality
- Implement ETL processes and data warehousing solutions

Required Skills:
- 5+ years of experience in data engineering
- Proficiency in Python, SQL, and data processing frameworks
- Experience with cloud platforms (AWS preferred)
- Knowledge of Apache Spark, Kafka, or similar technologies
- Strong problem-solving and communication skills
- Bachelor's degree in Computer Science or related field

Preferred Qualifications:
- Experience with machine learning pipelines
- Knowledge of containerization (Docker, Kubernetes)
- Familiarity with data visualization tools
- Previous experience in agile development environments
        '''
    }
    
    # Sample Resume
    sample_resume = {
        'filename': 'John_Doe_Resume.pdf',
        'candidate_name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '+1-555-0123',
        'content': '''
JOHN DOE
Data Engineer | Python Developer

EXPERIENCE:
Senior Data Analyst - DataTech Inc. (2020-2023)
- Developed Python scripts for data processing and analysis
- Created SQL queries for database optimization
- Worked with AWS services for cloud-based solutions
- Collaborated with cross-functional teams on data projects

Data Analyst - StartupCorp (2018-2020)
- Built ETL pipelines using Python and SQL
- Analyzed large datasets to provide business insights
- Created dashboards and reports for stakeholders

SKILLS:
- Programming: Python, SQL, JavaScript
- Cloud: AWS (EC2, S3, RDS), basic Azure knowledge
- Databases: PostgreSQL, MySQL, MongoDB
- Tools: Apache Spark, Docker, Git
- Analytics: Pandas, NumPy, Matplotlib

EDUCATION:
Bachelor of Science in Computer Science
University of Technology (2014-2018)

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Python Data Analysis Certification
        '''
    }
    
    try:
        # Insert sample data
        print("📄 Adding sample job description...")
        jd_id = db.insert_job_description(
            filename=sample_jd['filename'],
            company=sample_jd['company'],
            role=sample_jd['role'],
            location=sample_jd['location'],
            content=sample_jd['content']
        )
        
        print("👤 Adding sample resume...")
        resume_id = db.insert_resume(
            filename=sample_resume['filename'],
            candidate_name=sample_resume['candidate_name'],
            email=sample_resume['email'],
            job_role='Senior Data Engineer',  # Required parameter
            phone=sample_resume['phone'],
            content=sample_resume['content']
        )
        
        # Run semantic analysis
        print("🔍 Running semantic analysis...")
        analyzer = SemanticSearchService(db)
        
        # Analyze the resume against job description
        analysis_result = analyzer.analyze_resume_semantic(
            resume_text=sample_resume['content'],
            jd_text=sample_jd['content'],
            resume_id=resume_id,
            jd_id=jd_id
        )
        
        # Store analysis result
        print("💾 Storing analysis results...")
        db.insert_analysis_result(
            resume_id=resume_id,
            job_description_id=jd_id,
            relevance_score=analysis_result['relevance'],
            verdict=analysis_result['verdict'],
            missing_keywords=analysis_result['missing_keywords'],
            technical_skills=analysis_result.get('technical_skills', {}),
            soft_skills=analysis_result.get('soft_skills', {})
        )
        
        print("✅ Demo data initialization completed successfully!")
        print(f"📊 Analysis Result: {analysis_result['relevance']:.1f}% - {analysis_result['verdict']}")
        print(f"🔍 Missing Keywords: {len(analysis_result['missing_keywords'])} identified")
        
    except Exception as e:
        print(f"❌ Error initializing demo data: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    init_demo_data()