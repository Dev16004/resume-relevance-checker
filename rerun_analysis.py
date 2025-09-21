#!/usr/bin/env python3
"""
Re-run analysis to update database with correct scores and missing keywords
"""

import sqlite3
from database import DatabaseManager
from semantic_search import SemanticSearchService

def rerun_analysis():
    print("=== Re-running Analysis with Fixed Logic ===")
    
    # Initialize services
    db_manager = DatabaseManager()
    semantic_service = SemanticSearchService(db_manager)
    
    # Get all resumes and job descriptions
    resumes = db_manager.get_resumes()
    job_descriptions = db_manager.get_job_descriptions()
    
    print(f"📄 Found {len(resumes)} resumes")
    print(f"📋 Found {len(job_descriptions)} job descriptions")
    
    # Re-analyze each combination
    for resume in resumes:
        for jd in job_descriptions:
            print(f"\n🔍 Analyzing: {resume['candidate_name']} vs {jd['company']} - {jd['role']}")
            
            try:
                # Run semantic analysis
                result = semantic_service.analyze_resume_semantic(
                    resume_text=resume['content'],
                    jd_text=jd['content'],
                    resume_id=resume['id'],
                    jd_id=jd['id']
                )
                
                # Save updated result
                analysis_id = db_manager.insert_analysis_result(
                    resume_id=resume['id'],
                    job_description_id=jd['id'],
                    relevance_score=result['relevance'],
                    verdict=result['verdict'],
                    missing_keywords=result['missing_keywords'],
                    technical_skills=result['technical_skills'],
                    soft_skills=result['soft_skills']
                )
                
                print(f"✅ Updated analysis {analysis_id}")
                print(f"   📊 Score: {result['relevance']}%")
                print(f"   📝 Verdict: {result['verdict']}")
                print(f"   🔍 Missing Keywords: {result['missing_keywords']}")
                
            except Exception as e:
                print(f"❌ Error analyzing {resume['candidate_name']} vs {jd['company']}: {e}")
    
    print("\n🎉 Analysis update completed!")

if __name__ == "__main__":
    rerun_analysis()