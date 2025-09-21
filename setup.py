#!/usr/bin/env python3
"""
Setup script for Resume Relevance Checker
This script handles initial setup including NLTK data download
"""

import os
import sys
import subprocess
import nltk
from pathlib import Path

def install_requirements():
    """Install required packages from requirements.txt"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    try:
        # Create NLTK data directory
        nltk_data_dir = Path("./nltk_data")
        nltk_data_dir.mkdir(exist_ok=True)
        
        # Set NLTK data path
        nltk.data.path.append(str(nltk_data_dir))
        
        # Download required NLTK data
        nltk_packages = [
            'punkt',
            'stopwords', 
            'wordnet',
            'averaged_perceptron_tagger',
            'vader_lexicon'
        ]
        
        for package in nltk_packages:
            try:
                print(f"  Downloading {package}...")
                nltk.download(package, download_dir=str(nltk_data_dir))
            except Exception as e:
                print(f"  ⚠️  Warning: Could not download {package}: {e}")
        
        print("✅ NLTK data downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    directories = [
        "uploads",
        "chroma_db", 
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("✅ Directories created successfully!")

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from example...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created! Please edit it with your configuration.")
    else:
        print("ℹ️  .env file already exists or .env.example not found")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible!")
        print("   Please use Python 3.8 or higher")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Resume Relevance Checker...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during requirements installation")
        sys.exit(1)
    
    # Download NLTK data
    if not download_nltk_data():
        print("⚠️  NLTK data download failed, but continuing...")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()