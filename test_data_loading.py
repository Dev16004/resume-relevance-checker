#!/usr/bin/env python3
"""
Test script to check data loading from database
"""

from database import DatabaseManager

def test_data_loading():
    """Test if data loading functions work correctly"""
    print("🔍 Testing data loading functions...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Test each function
    print("\n📄 Testing get_resumes():")
    resume_data = db.get_resumes()
    print(f"   Result: {len(resume_data) if resume_data else 0} resumes found")
    if resume_data:
        for resume in resume_data:
            print(f"   - ID: {resume.get('id')}, Name: {resume.get('candidate_name')}")
    
    print("\n📋 Testing get_job_descriptions():")
    jd_data = db.get_job_descriptions()
    print(f"   Result: {len(jd_data) if jd_data else 0} job descriptions found")
    if jd_data:
        for jd in jd_data:
            print(f"   - ID: {jd.get('id')}, Company: {jd.get('company')}, Role: {jd.get('role')}")
    
    print("\n📊 Testing get_analysis_results():")
    analysis_results = db.get_analysis_results()
    print(f"   Result: {len(analysis_results) if analysis_results else 0} analysis results found")
    if analysis_results:
        for result in analysis_results:
            print(f"   - ID: {result.get('id')}, Resume ID: {result.get('resume_id')}, Score: {result.get('relevance_score')}")
    
    # Test boolean conditions
    print(f"\n🔍 Boolean checks:")
    print(f"   resume_data truthy: {bool(resume_data)}")
    print(f"   jd_data truthy: {bool(jd_data)}")
    print(f"   analysis_results truthy: {bool(analysis_results)}")
    
    return resume_data, jd_data, analysis_results

if __name__ == "__main__":
    test_data_loading()