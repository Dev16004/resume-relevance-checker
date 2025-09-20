# resume-relevance-check
# 🎯 AI-Powered Resume Checker

An intelligent resume analysis system that uses AI and machine learning to evaluate resumes against job descriptions, providing detailed insights and recommendations for candidates and recruiters.

## 📋 Table of Contents
- [Problem Statement](#problem-statement)
- [Approach & Solution](#approach--solution)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Problem Statement

In today's competitive job market, both job seekers and recruiters face significant challenges:

### For Job Seekers:
- **Lack of Feedback**: Candidates often receive no feedback on why their resumes were rejected
- **Skills Gap Identification**: Difficulty in understanding which skills are missing for specific roles
- **Resume Optimization**: No clear guidance on how to improve resume content and structure
- **Job Matching**: Uncertainty about how well their profile matches job requirements

### For Recruiters:
- **Volume Overload**: Processing hundreds of resumes manually is time-consuming
- **Inconsistent Evaluation**: Different recruiters may evaluate the same resume differently
- **Skill Assessment**: Difficulty in quickly identifying relevant skills and experience
- **Bias Reduction**: Need for objective, data-driven candidate evaluation

## 🚀 Approach & Solution

Our AI-powered resume checker addresses these challenges through a comprehensive multi-step approach:

### 1. **Document Processing & Text Extraction**
- **PDF & DOCX Support**: Robust parsing of various resume formats
- **Content Cleaning**: Intelligent text preprocessing and normalization
- **Structure Recognition**: Identification of resume sections (education, experience, skills)

### 2. **AI-Powered Analysis Engine**
- **Semantic Understanding**: Uses advanced NLP models for context-aware text analysis
- **Vector Embeddings**: Converts text to high-dimensional vectors for similarity matching
- **Machine Learning**: Employs scikit-learn for pattern recognition and scoring

### 3. **Intelligent Matching Algorithm**
- **Job-Resume Alignment**: Calculates relevance scores based on job requirements
- **Skills Gap Analysis**: Identifies missing skills and suggests improvements
- **Experience Mapping**: Matches candidate experience with job expectations

### 4. **Comprehensive Reporting**
- **Detailed Analytics**: Provides in-depth analysis with actionable insights
- **Visual Dashboards**: Interactive charts and graphs for easy understanding
- **Recommendation Engine**: Suggests specific improvements for better job matching

## ✨ Features

### 🔍 **Resume Analysis**
- **Multi-format Support**: PDF, DOCX, and TXT file processing
- **Content Extraction**: Intelligent parsing of resume sections
- **Skills Detection**: Automatic identification of technical and soft skills
- **Experience Analysis**: Evaluation of work history and achievements

### 📊 **Job Matching**
- **Relevance Scoring**: AI-calculated match percentage with job descriptions
- **Skills Comparison**: Side-by-side analysis of required vs. available skills
- **Gap Identification**: Clear highlighting of missing qualifications
- **Improvement Suggestions**: Specific recommendations for resume enhancement

### 📈 **Analytics Dashboard**
- **Performance Metrics**: Comprehensive scoring across multiple dimensions
- **Visual Insights**: Interactive charts and data visualizations
- **Candidate Comparison**: Benchmarking against other applicants
- **Trend Analysis**: Historical performance tracking

### 🎯 **Smart Recommendations**
- **Skill Development**: Targeted suggestions for skill improvement
- **Content Optimization**: Resume writing and formatting tips
- **Job Targeting**: Recommendations for suitable job opportunities
- **Career Guidance**: Strategic advice for career advancement

## 🛠 Technology Stack

### **Frontend**
- **Streamlit**: Modern web application framework for rapid development
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Data visualization and charting
- **Pillow**: Image processing capabilities

### **Backend**
- **Flask**: Lightweight web framework for API development
- **SQLite**: Embedded database for data storage
- **ChromaDB**: Vector database for semantic search

### **AI & Machine Learning**
- **spaCy**: Advanced natural language processing
- **NLTK**: Natural language toolkit for text processing
- **scikit-learn**: Machine learning algorithms and tools
- **Sentence Transformers**: State-of-the-art text embeddings

### **Document Processing**
- **PyMuPDF**: PDF text extraction and processing
- **python-docx**: Microsoft Word document handling
- **docx2txt**: Alternative DOCX text extraction

### **Additional Tools**
- **OpenCV**: Computer vision for document analysis
- **NumPy**: Numerical computing foundation
- **Requests**: HTTP library for API communications

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-checker.git
cd ai-resume-checker
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download Required Models
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 5: Initialize Database
```bash
python database.py
```

## 📖 Usage

### Starting the Application

#### Option 1: Run Both Services Separately
```bash
# Terminal 1: Start the backend server
python backend.py

# Terminal 2: Start the frontend application
streamlit run app.py
```

#### Option 2: Quick Start (Windows)
```bash
Start-Process python -ArgumentList "backend.py" -NoNewWindow; streamlit run app.py
```

### Accessing the Application
1. Open your web browser
2. Navigate to `http://localhost:8501`
3. The application interface will load automatically

### Using the Resume Checker

#### 1. **Upload Job Description**
- Navigate to the "Upload Job Description" tab
- Paste the job description text or upload a file
- Click "Save Job Description"

#### 2. **Upload Resumes**
- Go to the "Upload Resume" tab
- Select PDF or DOCX resume files
- Upload single or multiple resumes
- Wait for processing completion

#### 3. **Analyze Resumes**
- Click "Analyze Resume" for each uploaded resume
- The system will process and generate insights
- View real-time analysis progress

#### 4. **View Results**
- Navigate to the "Results" tab
- Explore comprehensive analytics:
  - **Dashboard Overview**: Key metrics and statistics
  - **Resume Analysis**: Detailed individual assessments
  - **Job Role Insights**: Performance across different roles
  - **Candidate Feedback**: Personalized recommendations

### Key Features in Action

#### **Dashboard Overview**
- Total resumes processed
- Average relevance scores
- Skills distribution analysis
- Performance trends

#### **Resume Analysis**
- Individual resume scores
- Skills matching percentage
- Experience relevance
- Improvement recommendations

#### **Job Role Insights**
- Role-specific performance metrics
- Skills gap analysis
- Candidate ranking
- Hiring recommendations

#### **Candidate Feedback**
- Personalized improvement suggestions
- Skills development roadmap
- Resume optimization tips
- Career guidance

## 📁 Project Structure

```
ai-resume-checker/
├── 📄 app.py                 # Main Streamlit application
├── 🔧 backend.py             # Flask backend server
├── 🗄️ database.py            # Database operations and models
├── ⚙️ config.py              # Configuration settings
├── 🔌 api_connector.py       # API integration layer
├── 🧠 embedding_service.py   # AI embedding generation
├── 🔍 semantic_search.py     # Semantic search functionality
├── 📊 vector_store.py        # Vector database operations
├── 📋 requirements.txt       # Python dependencies
├── 📖 README.md              # Project documentation
├── 📁 pages/                 # Streamlit page components
│   ├── 📄 upload_jd.py       # Job description upload
│   ├── 📄 upload_resume.py   # Resume upload interface
│   ├── 📊 results.py         # Results dashboard
│   └── 📝 omr_evaluation.py  # OMR sheet evaluation
├── 📁 uploads/               # File storage directory
│   ├── 📁 resumes/           # Uploaded resume files
│   ├── 📁 job_descriptions/  # Job description files
│   └── 📁 omr_sheets/        # OMR evaluation sheets
├── 🗄️ chroma_db/             # Vector database storage
├── 🗄️ resume_checker.db      # SQLite database file
└── 🐍 venv/                  # Virtual environment
```

## 🔧 API Documentation

### Backend Endpoints

#### Resume Operations
```http
POST /upload_resume
Content-Type: multipart/form-data
```

#### Job Description Operations
```http
POST /upload_job_description
Content-Type: application/json
```

#### Analysis Operations
```http
POST /analyze_resume
Content-Type: application/json
```

#### Data Retrieval
```http
GET /get_resumes
GET /get_job_descriptions
GET /get_analysis_results
```

### Database Schema

#### Resumes Table
- `id`: Primary key
- `filename`: Original file name
- `candidate_name`: Extracted candidate name
- `email`: Contact email
- `phone`: Phone number
- `content`: Extracted text content
- `upload_date`: Timestamp

#### Job Descriptions Table
- `id`: Primary key
- `filename`: File identifier
- `company`: Company name
- `role`: Job position
- `content`: Job description text
- `upload_date`: Timestamp

#### Analysis Results Table
- `id`: Primary key
- `resume_id`: Foreign key to resumes
- `job_description_id`: Foreign key to job descriptions
- `relevance_score`: AI-calculated match score
- `skills_match`: Skills alignment percentage
- `verdict`: Overall recommendation
- `analysis_date`: Timestamp

## 🤝 Contributing

We welcome contributions to improve the AI Resume Checker! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

### Areas for Contribution
- 🔍 Enhanced NLP models
- 📊 Additional visualization features
- 🔧 Performance optimizations
- 🌐 Multi-language support
- 📱 Mobile responsiveness
- 🔒 Security improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy Team**: For excellent NLP capabilities
- **Streamlit**: For the amazing web app framework
- **ChromaDB**: For efficient vector storage
- **Open Source Community**: For the incredible tools and libraries

## 📞 Support

If you encounter any issues or have questions:

1. **Check the Documentation**: Review this README and inline code comments
2. **Search Issues**: Look through existing GitHub issues
3. **Create an Issue**: Submit a detailed bug report or feature request
4. **Contact**: Reach out to the development team

---

**Made with ❤️ by the AI Resume Checker Team**

*Empowering careers through intelligent resume analysis*
