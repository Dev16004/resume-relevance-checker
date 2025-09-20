import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

class DatabaseManager:
    """Database manager for the Resume Checker application using SQLite"""
    
    def __init__(self, db_path: str = "resume_checker.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory for dict-like access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create job_descriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT NOT NULL,
                upload_date DATETIME NOT NULL,
                status TEXT DEFAULT 'Active',
                content TEXT,
                has_embedding BOOLEAN DEFAULT FALSE,
                embedding_model TEXT,
                embedding_created_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create resumes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                candidate_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                job_role TEXT NOT NULL,
                upload_date DATETIME NOT NULL,
                status TEXT DEFAULT 'Pending Review',
                content TEXT,
                has_embedding BOOLEAN DEFAULT FALSE,
                embedding_model TEXT,
                embedding_created_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analysis_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_description_id INTEGER NOT NULL,
                relevance_score REAL NOT NULL,
                verdict TEXT NOT NULL,
                missing_keywords TEXT,  -- JSON array
                technical_skills TEXT,  -- JSON object
                soft_skills TEXT,       -- JSON object
                analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id),
                UNIQUE(resume_id, job_description_id)
            )
        ''')
        
        # Create skills table for better skill management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,  -- 'technical' or 'soft'
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create resume_skills junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                proficiency_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (skill_id) REFERENCES skills (id),
                UNIQUE(resume_id, skill_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_job_role ON resumes(job_role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jd_status ON job_descriptions(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_resume_id ON analysis_results(resume_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_jd_id ON analysis_results(job_description_id)')
        
        conn.commit()
        conn.close()
    
    # Job Description Operations
    def insert_job_description(self, filename: str, company: str, role: str, 
                             location: str, content: str = None) -> int:
        """Insert a new job description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now()
        cursor.execute('''
            INSERT INTO job_descriptions 
            (filename, company, role, location, upload_date, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, company, role, location, upload_date, content))
        
        jd_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jd_id
    
    def get_job_descriptions(self, status: str = None) -> List[Dict]:
        """Get all job descriptions, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM job_descriptions WHERE status = ? ORDER BY upload_date DESC', (status,))
        else:
            cursor.execute('SELECT * FROM job_descriptions ORDER BY upload_date DESC')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_job_description_by_id(self, jd_id: int) -> Optional[Dict]:
        """Get a job description by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (jd_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_job_description_by_filename(self, filename: str) -> Optional[Dict]:
        """Get a job description by filename"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_descriptions WHERE filename = ?', (filename,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def update_job_description_status(self, jd_id: int, status: str) -> bool:
        """Update job description status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE job_descriptions 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, jd_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_job_description(self, jd_id: int) -> bool:
        """Delete a job description and related analysis results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete related analysis results first
        cursor.execute('DELETE FROM analysis_results WHERE job_description_id = ?', (jd_id,))
        # Delete the job description
        cursor.execute('DELETE FROM job_descriptions WHERE id = ?', (jd_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Resume Operations
    def insert_resume(self, filename: str, candidate_name: str, email: str, 
                     job_role: str, phone: str = None, content: str = None) -> int:
        """Insert a new resume"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now()
        cursor.execute('''
            INSERT INTO resumes 
            (filename, candidate_name, email, phone, job_role, upload_date, content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, candidate_name, email, phone, job_role, upload_date, content))
        
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return resume_id
    
    def get_resumes(self, job_role: str = None, status: str = None) -> List[Dict]:
        """Get all resumes, optionally filtered by job role and status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM resumes WHERE 1=1'
        params = []
        
        if job_role:
            query += ' AND job_role = ?'
            params.append(job_role)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY upload_date DESC'
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_resume_by_id(self, resume_id: int) -> Optional[Dict]:
        """Get a resume by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_resume_by_filename(self, filename: str) -> Optional[Dict]:
        """Get a resume by filename"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE filename = ?', (filename,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def update_resume_status(self, resume_id: int, status: str) -> bool:
        """Update resume status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE resumes 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, resume_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Analysis Results Operations
    def insert_analysis_result(self, resume_id: int, job_description_id: int,
                             relevance_score: float, verdict: str,
                             missing_keywords: List[str] = None,
                             technical_skills: Dict = None,
                             soft_skills: Dict = None) -> int:
        """Insert or update an analysis result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert lists/dicts to JSON strings
        missing_keywords_json = json.dumps(missing_keywords or [])
        technical_skills_json = json.dumps(technical_skills or {})
        soft_skills_json = json.dumps(soft_skills or {})
        
        cursor.execute('''
            INSERT OR REPLACE INTO analysis_results 
            (resume_id, job_description_id, relevance_score, verdict, 
             missing_keywords, technical_skills, soft_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (resume_id, job_description_id, relevance_score, verdict,
              missing_keywords_json, technical_skills_json, soft_skills_json))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def get_analysis_results(self, resume_id: int = None, 
                           job_description_id: int = None) -> List[Dict]:
        """Get analysis results with optional filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT ar.*, r.candidate_name, r.filename as resume_filename,
                   jd.company, jd.role, jd.filename as jd_filename
            FROM analysis_results ar
            JOIN resumes r ON ar.resume_id = r.id
            JOIN job_descriptions jd ON ar.job_description_id = jd.id
            WHERE 1=1
        '''
        params = []
        
        if resume_id:
            query += ' AND ar.resume_id = ?'
            params.append(resume_id)
        
        if job_description_id:
            query += ' AND ar.job_description_id = ?'
            params.append(job_description_id)
        
        query += ' ORDER BY ar.analysis_date DESC'
        
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON fields
            result['missing_keywords'] = json.loads(result['missing_keywords'])
            result['technical_skills'] = json.loads(result['technical_skills'])
            result['soft_skills'] = json.loads(result['soft_skills'])
            results.append(result)
        
        conn.close()
        return results
    
    # Statistics and Analytics
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total counts
        cursor.execute('SELECT COUNT(*) FROM resumes')
        total_resumes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM job_descriptions WHERE status = "Active"')
        active_jds = cursor.fetchone()[0]
        
        # Average relevance score
        cursor.execute('SELECT AVG(relevance_score) FROM analysis_results')
        avg_score = cursor.fetchone()[0] or 0
        
        # High suitability matches
        cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE verdict = "High"')
        high_matches = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_resumes': total_resumes,
            'active_job_descriptions': active_jds,
            'average_relevance_score': round(avg_score, 1),
            'high_suitability_matches': high_matches
        }
    
    def get_job_role_metrics(self) -> List[Dict]:
        """Get metrics grouped by job role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                r.job_role,
                COUNT(r.id) as resume_count,
                AVG(ar.relevance_score) as avg_score,
                MIN(ar.relevance_score) as min_score,
                MAX(ar.relevance_score) as max_score,
                COUNT(CASE WHEN ar.verdict = 'High' THEN 1 END) as high_count
            FROM resumes r
            LEFT JOIN analysis_results ar ON r.id = ar.resume_id
            GROUP BY r.job_role
            ORDER BY avg_score DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            if result['resume_count'] > 0:
                result['high_match_percent'] = round(
                    (result['high_count'] / result['resume_count']) * 100, 1
                )
            else:
                result['high_match_percent'] = 0
            results.append(result)
        
        conn.close()
        return results
    
    # Migration helper
    def migrate_from_csv(self, csv_data: List[Dict], table_type: str) -> int:
        """Migrate data from CSV format to database"""
        migrated_count = 0
        
        if table_type == 'resumes':
            for row in csv_data:
                try:
                    self.insert_resume(
                        filename=row.get('filename', ''),
                        candidate_name=row.get('candidate_name', ''),
                        email=row.get('email', ''),
                        job_role=row.get('job_role', ''),
                        phone=row.get('phone', '')
                    )
                    migrated_count += 1
                except Exception as e:
                    print(f"Error migrating resume {row.get('filename', '')}: {e}")
        
        elif table_type == 'job_descriptions':
            for row in csv_data:
                try:
                    self.insert_job_description(
                        filename=row.get('filename', ''),
                        company=row.get('company', ''),
                        role=row.get('role', ''),
                        location=row.get('location', '')
                    )
                    migrated_count += 1
                except Exception as e:
                    print(f"Error migrating JD {row.get('filename', '')}: {e}")
        
        return migrated_count
    
    # Embedding Management Methods
    def update_resume_embedding_status(self, resume_id: int, model_name: str) -> bool:
        """Update resume embedding status after embedding is created"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE resumes 
            SET has_embedding = TRUE, 
                embedding_model = ?, 
                embedding_created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (model_name, resume_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def update_job_description_embedding_status(self, jd_id: int, model_name: str) -> bool:
        """Update job description embedding status after embedding is created"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE job_descriptions 
            SET has_embedding = TRUE, 
                embedding_model = ?, 
                embedding_created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (model_name, jd_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_resumes_without_embeddings(self) -> List[Dict]:
        """Get all resumes that don't have embeddings yet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM resumes 
            WHERE has_embedding = FALSE OR has_embedding IS NULL
            ORDER BY created_at DESC
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_job_descriptions_without_embeddings(self) -> List[Dict]:
        """Get all job descriptions that don't have embeddings yet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM job_descriptions 
            WHERE has_embedding = FALSE OR has_embedding IS NULL
            ORDER BY created_at DESC
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results