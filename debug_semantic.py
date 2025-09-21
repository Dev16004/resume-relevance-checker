#!/usr/bin/env python3
"""
Debug script to test semantic keyword extraction
"""

import sqlite3
import json
from semantic_search import SemanticSearchService
from database import DatabaseManager

def debug_semantic_analysis():
    print("=== Debugging Semantic Analysis ===")
    
    # Initialize database manager and semantic search service
    db_manager = DatabaseManager()
    semantic_service = SemanticSearchService(db_manager)
    
    # Get data from database
    conn = sqlite3.connect('resume_checker.db')
    cursor = conn.cursor()
    
    # Get a resume and job description
    cursor.execute("SELECT content FROM resumes LIMIT 1")
    resume_result = cursor.fetchone()
    
    cursor.execute("SELECT content FROM job_descriptions LIMIT 1")
    jd_result = cursor.fetchone()
    
    if not resume_result or not jd_result:
        print("❌ No resume or job description found in database")
        return
    
    resume_text = resume_result[0]
    jd_text = jd_result[0]
    
    print(f"📄 Resume length: {len(resume_text)} characters")
    print(f"📋 Job description length: {len(jd_text)} characters")
    print()
    
    # Test the semantic analysis
    try:
        print("🔍 Running semantic analysis...")
        result = semantic_service.analyze_resume_semantic(resume_text, jd_text)
        
        print(f"✅ Analysis completed!")
        print(f"📊 Relevance Score: {result.get('relevance', 'N/A')}%")
        print(f"📊 Relevance Score (alt): {result.get('relevance_score', 'N/A')}%")
        print(f"📝 Verdict: {result.get('verdict', 'N/A')}")
        print(f"🔍 Missing Keywords: {result.get('missing_keywords', [])}")
        print(f"🎯 Technical Skills: {result.get('technical_skills', 'N/A')}")
        print(f"💼 Soft Skills: {result.get('soft_skills', 'N/A')}")
        print(f"🔢 Similarity Score: {result.get('similarity_score', 'N/A')}")
        
        # Test the keyword extraction specifically
        print("\n🔧 Testing keyword extraction directly...")
        missing_keywords = semantic_service._extract_semantic_keywords(resume_text, jd_text)
        print(f"🔍 Direct keyword extraction result: {missing_keywords}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    debug_semantic_analysis()