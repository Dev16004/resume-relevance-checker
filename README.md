# Resume Relevance Checker

A comprehensive AI-powered resume analysis tool that evaluates resume-job description compatibility using advanced semantic search and machine learning techniques.

## 🚀 Features

- **Resume Upload & Analysis**: Support for PDF and DOCX formats
- **Job Description Processing**: Intelligent JD parsing and analysis
- **Semantic Matching**: Advanced AI-powered similarity scoring
- **Skills Analysis**: Technical and soft skills extraction
- **Interactive Dashboard**: User-friendly Streamlit interface
- **RESTful API**: Backend API for programmatic access
- **Vector Search**: ChromaDB-powered semantic search (with fallback)
- **Database Management**: SQLite-based data persistence

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Flask
- **AI/ML**: Sentence Transformers, NLTK
- **Vector Database**: ChromaDB
- **Database**: SQLite
- **Document Processing**: PyMuPDF, python-docx, docx2txt
- **Deployment**: Streamlit Cloud compatible

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning)

## 🔧 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/resume-relevance-checker.git
   cd resume-relevance-checker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (first run only)
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

5. **Run the application**
   ```bash
   # Start the Streamlit app
   streamlit run app.py
   
   # In another terminal, start the backend (optional)
   python backend.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:8501`

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app.py` as the main file
   - Deploy!

### Environment Variables

For production deployment, set these environment variables:
- `PYTHONPATH`: Set to project root
- `NLTK_DATA`: Path to NLTK data directory

## 📁 Project Structure

```
resume-relevance-checker/
├── app.py                 # Main Streamlit application
├── backend.py            # Flask API backend
├── requirements.txt      # Python dependencies
├── config.py            # Configuration settings
├── database.py          # Database management
├── embedding_service.py # AI embedding service
├── semantic_search.py   # Semantic search logic
├── vector_store.py      # Vector database operations
├── api_connector.py     # API connection utilities
├── pages/               # Streamlit pages
│   ├── upload_resume.py
│   ├── upload_jd.py
│   ├── results.py
│   └── omr_evaluation.py
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔍 Usage

### Web Interface

1. **Upload Resume**: Navigate to "Upload Resume" page and upload PDF/DOCX files
2. **Upload Job Description**: Go to "Upload Job Description" and paste or upload JD
3. **View Results**: Check the "Results" page for analysis and matching scores
4. **OMR Evaluation**: Use the evaluation page for detailed assessments

### API Usage

The Flask backend provides RESTful endpoints:

```python
# Example API calls
import requests

# Upload resume
files = {'file': open('resume.pdf', 'rb')}
response = requests.post('http://localhost:5000/upload_resume', files=files)

# Get analysis
response = requests.get('http://localhost:5000/analyze/resume_id/jd_id')
```

## 🛡️ Error Handling

The application includes robust error handling:
- **ChromaDB Fallback**: Graceful degradation when vector database is unavailable
- **File Processing**: Comprehensive error handling for document parsing
- **API Resilience**: Fallback mechanisms for all external dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

1. **ChromaDB Import Error**
   - The app includes fallback mechanisms
   - Vector search will be disabled but core functionality remains

2. **NLTK Data Missing**
   ```python
   import nltk
   nltk.download('all')
   ```

3. **Memory Issues**
   - Reduce batch sizes in config.py
   - Use lighter embedding models

### Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the logs for detailed error messages

## 🔄 Updates

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added ChromaDB fallback mechanisms
- **v1.2.0**: Enhanced error handling and deployment readiness

---

**Made with ❤️ for better recruitment processes**