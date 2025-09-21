#!/usr/bin/env python3
"""
Debug script to test keyword extraction specifically
"""

import sqlite3
import json
import numpy as np
from semantic_search import SemanticSearchService
from database import DatabaseManager

def debug_keyword_extraction():
    print("=== Debugging Keyword Extraction ===")
    
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
    
    try:
        # Generate embeddings
        print("🔍 Generating embeddings...")
        resume_embedding = semantic_service.embedding_service.generate_embedding(resume_text)
        jd_embedding = semantic_service.embedding_service.generate_embedding(jd_text)
        
        print(f"✅ Resume embedding shape: {resume_embedding.shape}")
        print(f"✅ JD embedding shape: {jd_embedding.shape}")
        
        # Test overall similarity
        overall_similarity = semantic_service.embedding_service.calculate_similarity(
            resume_embedding, jd_embedding
        )
        print(f"📊 Overall similarity: {overall_similarity:.4f}")
        print()
        
        # Test keyword extraction step by step
        print("🔧 Testing keyword extraction step by step...")
        
        # Split JD into sentences
        jd_sentences = [s.strip() for s in jd_text.split('.') if len(s.strip()) > 10]
        print(f"📝 Found {len(jd_sentences)} sentences in JD")
        
        missing_concepts = []
        
        # Test first 5 sentences
        for i, sentence in enumerate(jd_sentences[:5]):
            print(f"\n--- Sentence {i+1} ---")
            print(f"Text: {sentence[:100]}...")
            
            sentence_embedding = semantic_service.embedding_service.generate_embedding(sentence)
            similarity = semantic_service.embedding_service.calculate_similarity(
                sentence_embedding, resume_embedding
            )
            
            print(f"Similarity: {similarity:.4f}")
            
            if similarity < 0.3:
                print("❌ Below threshold (0.3) - Missing concept!")
                words = sentence.lower().split()
                key_words = [w for w in words if len(w) > 3 and w.isalpha()]
                print(f"Key words: {key_words[:3]}")
                missing_concepts.extend(key_words[:3])
            else:
                print("✅ Above threshold - Concept found in resume")
        
        print(f"\n🔍 Final missing concepts: {list(set(missing_concepts))}")
        
        # Test with different thresholds
        print("\n🎯 Testing different thresholds:")
        for threshold in [0.1, 0.2, 0.3, 0.4, 0.5]:
            missing_count = 0
            for sentence in jd_sentences[:10]:
                sentence_embedding = semantic_service.embedding_service.generate_embedding(sentence)
                similarity = semantic_service.embedding_service.calculate_similarity(
                    sentence_embedding, resume_embedding
                )
                if similarity < threshold:
                    missing_count += 1
            print(f"Threshold {threshold}: {missing_count}/10 sentences below threshold")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    debug_keyword_extraction()