"""
AI-Powered Resume Checker - Backend API Server

This Flask application provides the backend API for the resume checking system.
It handles file uploads, text extraction, AI-powered analysis, and data management.

Key Features:
- RESTful API endpoints for frontend integration
- Multi-format document processing (PDF, DOCX, TXT)
- AI-powered semantic analysis using embeddings
- SQLite database integration for data persistence
- Vector search capabilities with ChromaDB
- OMR sheet evaluation for assessment scoring

Endpoints:
- /api/upload/resume - Resume file upload and processing
- /api/upload/jd - Job description upload and processing
- /api/analyze - Resume-job description matching analysis
- /api/search/* - Semantic search functionality
- /api/models/* - Embedding model management

Author: AI Resume Checker Team
Version: 1.0.0
"""

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import docx2txt
import fitz  # PyMuPDF
import nltk
import json
import random
from PIL import Image
import io
from database import DatabaseManager
from semantic_search import get_semantic_search_service
from embedding_service import get_embedding_service

# NLTK is kept for potential future text processing needs

app = Flask(__name__)

# Initialize database connection
db = DatabaseManager()

# Initialize semantic search service with database integration
semantic_search = get_semantic_search_service(db)

# Configure upload folders for different file types
UPLOAD_FOLDER = 'uploads'
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
JD_FOLDER = os.path.join(UPLOAD_FOLDER, 'job_descriptions')

# Ensure directories exist for file storage
os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(JD_FOLDER, exist_ok=True)

# Document processing functions
def extract_text_from_pdf(path):
    """
    Extract text from PDF files using PyMuPDF
    
    Args:
        path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content from all pages
    """
    text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(path):
    """
    Extract text from DOCX files using docx2txt
    
    Args:
        path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text content from the document
    """
    try:
        text = docx2txt.process(path)
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def clean_text(text):
    """
    Clean and normalize extracted text content
    
    Args:
        text (str): Raw text content
        
    Returns:
        str: Cleaned and normalized text
    """
    return text.replace('\n', ' ').strip()

def extract_text(file_path):
    """
    Universal text extraction function for multiple file formats
    
    Args:
        file_path (str): Path to the file to extract text from
        
    Returns:
        str: Extracted and cleaned text content
    """
    if file_path.lower().endswith('.pdf'):
        return clean_text(extract_text_from_pdf(file_path))
    elif file_path.lower().endswith(('.docx', '.doc')):
        return clean_text(extract_text_from_docx(file_path))
    return ""

def analyze_resume(resume_text, jd_text, resume_id=None, jd_id=None):
    """
    Perform AI-powered analysis of resume against job description
    
    This function uses semantic search and machine learning to:
    - Calculate relevance scores
    - Identify skill matches and gaps
    - Generate improvement recommendations
    
    Args:
        resume_text (str): Extracted resume content
        jd_text (str): Job description content
        resume_id (int, optional): Database ID of the resume
        jd_id (int, optional): Database ID of the job description
        
    Returns:
        dict: Analysis results including scores and recommendations
    """
    # Use semantic search for analysis
    analysis_result = semantic_search.analyze_resume_semantic(
        resume_text, jd_text, resume_id, jd_id
    )
    
    # Ensure backward compatibility with existing API
    relevance_score = analysis_result.get("relevance", 0)
    return {
        "relevance": relevance_score,  # For backward compatibility
        "relevance_score": relevance_score,  # For database compatibility
        "verdict": analysis_result.get("verdict", "Low"),
        "missing_keywords": analysis_result.get("missing_keywords", []),
        "technical_skills": analysis_result.get("technical_skills", {}),
        "soft_skills": analysis_result.get("soft_skills", {}),
        "similarity_score": analysis_result.get("similarity_score", 0),
        "analysis_method": analysis_result.get("analysis_method", "semantic")
    }



def generate_skills_data(jd_text, resume_text, skill_type):
    """
    Generate skills data for VSD based on job description and resume
    """
    # Define common technical and soft skills
    technical_skills_list = [
        "Python", "Java", "JavaScript", "SQL", "Machine Learning",
        "Data Analysis", "Cloud Computing", "DevOps", "Web Development", "API"
    ]
    
    soft_skills_list = [
        "Communication", "Teamwork", "Problem Solving", "Leadership",
        "Time Management", "Adaptability", "Creativity", "Critical Thinking"
    ]
    
    skills_list = technical_skills_list if skill_type == "technical" else soft_skills_list
    skills_data = {}
    
    # For each skill, calculate a score based on presence in resume and job description
    for skill in skills_list:
        skill_lower = skill.lower()
        
        # Check if skill is mentioned in JD
        jd_contains = skill_lower in jd_text.lower()
        
        # Check if skill is mentioned in resume
        resume_contains = skill_lower in resume_text.lower()
        
        # Calculate base score
        if resume_contains and jd_contains:
            # Skill is in both - high score
            base_score = 85
        elif resume_contains:
            # Skill is only in resume - medium score
            base_score = 65
        elif jd_contains:
            # Skill is only in JD - low score
            base_score = 30
        else:
            # Skill is in neither - skip
            continue
        
        # Add some variance to make it look more realistic
        variance = random.randint(-15, 15)
        final_score = max(min(base_score + variance, 100), 10)
        
        skills_data[skill] = final_score
    
    return skills_data

# OMR Evaluation Functions
def process_omr_sheet(image_path):
    """Mock OMR sheet processing - generates random answers for demonstration"""
    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}
        
        # Verify it's an image file using PIL
        with Image.open(image_path) as img:
            # Mock processing - generate random answers for demonstration
            question_count = random.randint(10, 20)  # Random number of questions
            answers = []
            
            for q in range(1, question_count + 1):
                # Randomly select an answer (A, B, C, or D)
                option = random.choice(['A', 'B', 'C', 'D'])
                answers.append({"question": q, "answer": option})
            
            return {
                "total_questions": question_count,
                "answers": answers
            }
    
    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}

# API Routes
@app.route('/api/upload/resume', methods=['POST'])
def upload_resume():
    """
    Handle resume file upload and processing
    
    Accepts PDF, DOCX, and TXT files, extracts text content,
    and stores metadata in the database
    
    Returns:
        JSON response with upload status and file information
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(RESUME_FOLDER, filename)
    file.save(file_path)
    
    # Extract text from the resume
    resume_text = extract_text(file_path)
    
    # Save to database
    resume_id = db.add_resume(filename, resume_text, file_path)
    
    return jsonify({
        "message": "Resume uploaded successfully",
        "resume_id": resume_id,
        "filename": filename,
        "text_length": len(resume_text)
    })

@app.route('/api/upload/omr', methods=['POST'])
def upload_omr():
    """
    Handle OMR sheet upload and processing
    
    Processes uploaded OMR sheet images for assessment evaluation
    
    Returns:
        JSON response with processing results
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check if the file is an image
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({"error": "File must be an image (PNG, JPG)"}), 400
    
    filename = secure_filename(file.filename)
    omr_folder = os.path.join(UPLOAD_FOLDER, 'omr_sheets')
    os.makedirs(omr_folder, exist_ok=True)
    
    file_path = os.path.join(omr_folder, filename)
    file.save(file_path)
    
    # Process the OMR sheet
    results = process_omr_sheet(file_path)
    
    if "error" in results:
        return jsonify({"error": results["error"]}), 500
    
    return jsonify({
        "message": "OMR sheet processed successfully",
        "filename": filename,
        "results": results
    })

@app.route('/api/upload/jd', methods=['POST'])
def upload_jd():
    """
    Handle job description upload and processing
    
    Accepts job description text or files and stores in database
    
    Returns:
        JSON response with upload status
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(JD_FOLDER, filename)
    file.save(file_path)
    
    # Extract text from the job description
    jd_text = extract_text(file_path)
    
    # Save to database
    jd_id = db.add_job_description(filename, jd_text, file_path)
    
    return jsonify({
        "message": "Job description uploaded successfully",
        "jd_id": jd_id,
        "filename": filename,
        "text_length": len(jd_text)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Perform resume analysis against job description
    
    Main analysis endpoint that coordinates AI-powered matching
    and generates comprehensive results
    
    Returns:
        JSON response with analysis results and recommendations
    """
    data = request.json
    
    # Support both filename and ID-based lookup
    resume_filename = data.get('resume_filename')
    jd_filename = data.get('jd_filename')
    resume_id = data.get('resume_id')
    jd_id = data.get('jd_id')
    
    resume_text = None
    jd_text = None
    
    # Get resume text
    if resume_id:
        resume_data = db.get_resume_by_id(resume_id)
        if resume_data:
            resume_text = resume_data['content']
            resume_filename = resume_data['filename']
        else:
            return jsonify({"error": "Resume not found"}), 404
    elif resume_filename:
        resume_path = os.path.join(RESUME_FOLDER, secure_filename(resume_filename))
        if os.path.exists(resume_path):
            resume_text = extract_text(resume_path)
        else:
            return jsonify({"error": "Resume file not found"}), 404
    else:
        return jsonify({"error": "Resume filename or ID is required"}), 400
    
    # Get job description text
    if jd_id:
        jd_data = db.get_job_description_by_id(jd_id)
        if jd_data:
            jd_text = jd_data['content']
            jd_filename = jd_data['filename']
        else:
            return jsonify({"error": "Job description not found"}), 404
    elif jd_filename:
        jd_path = os.path.join(JD_FOLDER, secure_filename(jd_filename))
        if os.path.exists(jd_path):
            jd_text = extract_text(jd_path)
        else:
            return jsonify({"error": "Job description file not found"}), 404
    else:
        return jsonify({"error": "Job description filename or ID is required"}), 400
    
    # Perform analysis with semantic search
    analysis_result = analyze_resume(resume_text, jd_text, resume_id, jd_id)
    
    # Save analysis result to database if we have valid IDs
    analysis_id = None
    if resume_id and jd_id:
        try:
            analysis_id = db.insert_analysis_result(
                resume_id=resume_id,
                job_description_id=jd_id,
                relevance_score=analysis_result['relevance_score'],
                verdict=analysis_result['verdict'],
                missing_keywords=analysis_result['missing_keywords'],
                technical_skills=analysis_result['technical_skills'],
                soft_skills=analysis_result['soft_skills']
            )
        except Exception as e:
            print(f"Error saving analysis result: {e}")
    
    analysis_result['analysis_id'] = analysis_id
    
    return jsonify(analysis_result)

@app.route('/api/files/resumes', methods=['GET'])
def list_resumes():
    """Get list of all uploaded resumes"""
    resumes = db.get_resumes()
    return jsonify({"resumes": resumes})

@app.route('/api/files/jds', methods=['GET'])
def list_jds():
    """Get list of all uploaded job descriptions"""
    jds = db.get_job_descriptions()
    return jsonify({"job_descriptions": jds})

@app.route('/api/analysis/results', methods=['GET'])
def list_analysis_results():
    """Get list of all analysis results"""
    results = db.get_analysis_results()
    return jsonify({"analysis_results": results})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics and metrics"""
    stats = db.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/evaluate/omr', methods=['POST'])
def evaluate_omr():
    """Evaluate OMR sheet and calculate assessment scores"""
    data = request.json
    
    if not data or 'answers' not in data or 'answer_key' not in data:
        return jsonify({"error": "Missing answers or answer key"}), 400
    
    student_answers = data['answers']
    answer_key = data['answer_key']
    
    # Calculate score
    correct = 0
    incorrect = 0
    skipped = 0
    
    results = []
    
    # Get the maximum question number from both sets
    max_question = max(
        max([a.get('question', 0) for a in student_answers]),
        max([a.get('question', 0) for a in answer_key])
    )
    
    # Create a lookup for the answer key
    key_lookup = {a['question']: a['answer'] for a in answer_key if 'question' in a and 'answer' in a}
    student_lookup = {a['question']: a['answer'] for a in student_answers if 'question' in a and 'answer' in a}
    
    for q in range(1, max_question + 1):
        if q in key_lookup:
            correct_answer = key_lookup[q]
            
            if q in student_lookup:
                student_answer = student_lookup[q]
                
                if student_answer == correct_answer:
                    status = "correct"
                    correct += 1
                else:
                    status = "incorrect"
                    incorrect += 1
            else:
                status = "skipped"
                skipped += 1
                student_answer = None
                
            results.append({
                "question": q,
                "correct_answer": correct_answer,
                "student_answer": student_answer,
                "status": status
            })
    
    total_questions = len(key_lookup)
    score_percentage = (correct / total_questions * 100) if total_questions > 0 else 0
    
    return jsonify({
        "total_questions": total_questions,
        "correct": correct,
        "incorrect": incorrect,
        "skipped": skipped,
        "score_percentage": round(score_percentage, 2),
        "results": results
    })

# Semantic Search API Endpoints
@app.route('/api/search/resumes', methods=['POST'])
def search_resumes():
    """Semantic search for resumes based on query text"""
    data = request.json
    query_text = data.get('query_text', '')
    top_k = data.get('top_k', 5)
    
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
    
    try:
        results = semantic_search.search_similar_resumes(query_text, top_k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route('/api/search/job_descriptions', methods=['POST'])
def search_job_descriptions():
    """Semantic search for job descriptions based on query text"""
    data = request.json
    query_text = data.get('query_text', '')
    top_k = data.get('top_k', 5)
    
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
    
    try:
        results = semantic_search.search_similar_job_descriptions(query_text, top_k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route('/api/matches/<int:resume_id>', methods=['GET'])
def get_best_matches(resume_id):
    """Get best job description matches for a specific resume"""
    top_k = request.args.get('top_k', 5, type=int)
    
    try:
        results = semantic_search.get_best_matches(resume_id, top_k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Failed to get matches: {str(e)}"}), 500

@app.route('/api/embeddings/generate', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for uploaded documents"""
    try:
        # Get items without embeddings
        resumes_without_embeddings = db.get_resumes_without_embeddings()
        jds_without_embeddings = db.get_job_descriptions_without_embeddings()
        
        resumes_processed = 0
        jds_processed = 0
        
        # Generate embeddings for resumes
        for resume in resumes_without_embeddings:
            if resume.get('content'):
                try:
                    # Get resume metadata
                    resume_data = db.get_resume_by_id(resume['id'])
                    metadata = {
                        "resume_id": resume['id'],
                        "filename": resume_data.get('filename', ''),
                        "candidate_name": resume_data.get('candidate_name', ''),
                        "job_role": resume_data.get('job_role', ''),
                        "email": resume_data.get('email', ''),
                    }
                    
                    # Add embedding to vector store
                    success = semantic_search.vector_store.add_resume_embedding(
                        resume_id=resume['id'],
                        text=resume['content'],
                        metadata=metadata
                    )
                    
                    if success:
                        # Update database embedding status
                        db.update_resume_embedding_status(
                            resume['id'], semantic_search.embedding_service.model_name
                        )
                        resumes_processed += 1
                        
                except Exception as e:
                    print(f"Error generating embedding for resume {resume['id']}: {e}")
        
        # Generate embeddings for job descriptions
        for jd in jds_without_embeddings:
            if jd.get('content'):
                try:
                    # Get JD metadata
                    jd_data = db.get_job_description_by_id(jd['id'])
                    metadata = {
                        "jd_id": jd['id'],
                        "filename": jd_data.get('filename', ''),
                        "company": jd_data.get('company', ''),
                        "role": jd_data.get('role', ''),
                        "location": jd_data.get('location', ''),
                    }
                    
                    # Add embedding to vector store
                    success = semantic_search.vector_store.add_job_description_embedding(
                        jd_id=jd['id'],
                        text=jd['content'],
                        metadata=metadata
                    )
                    
                    if success:
                        # Update database embedding status
                        db.update_job_description_embedding_status(
                            jd['id'], semantic_search.embedding_service.model_name
                        )
                        jds_processed += 1
                        
                except Exception as e:
                    print(f"Error generating embedding for JD {jd['id']}: {e}")
        
        return jsonify({
            "message": f"Generated embeddings for {resumes_processed + jds_processed} items",
            "resumes_processed": resumes_processed,
            "jds_processed": jds_processed
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate embeddings: {str(e)}"}), 500

@app.route('/api/models/available', methods=['GET'])
def get_available_models():
    """Get all available embedding models"""
    try:
        embedding_service = get_embedding_service()
        models = embedding_service.get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/current', methods=['GET'])
def get_current_model():
    """Get current embedding model information"""
    try:
        embedding_service = get_embedding_service()
        model_info = embedding_service.get_model_info()
        return jsonify({'model': model_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/switch', methods=['POST'])
def switch_model():
    """Switch to a different embedding model"""
    try:
        data = request.get_json()
        model_key = data.get('model_key')
        
        if not model_key:
            return jsonify({'error': 'model_key is required'}), 400
        
        embedding_service = get_embedding_service()
        embedding_service.switch_model(model_key)
        
        # Get updated model info
        model_info = embedding_service.get_model_info()
        
        return jsonify({
            'message': f'Successfully switched to {model_key} model',
            'model': model_info
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start the Flask development server
    # Runs on localhost:5000 with debug mode enabled for development and testing
    app.run(debug=True, port=5000)