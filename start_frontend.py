#!/usr/bin/env python3
"""
Startup script for PII Processor Frontend

This script:
1. Checks for required dependencies
2. Installs missing dependencies if needed
3. Starts the Flask server
"""

import sys
import subprocess
import os
from pathlib import Path

def check_and_install_requirements():
    """Check and install required packages"""
    print("🔍 Checking dependencies...")
    
    required_packages = {
        'flask': 'Flask==2.3.3',
        'flask_cors': 'Flask-CORS==4.0.0', 
        'requests': 'requests==2.31.0'
    }
    
    missing_packages = []
    
    for package, requirement in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(requirement)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def check_frontend_files():
    """Check if frontend files exist"""
    frontend_dir = Path(__file__).parent / 'frontend'
    required_files = ['index.html', 'styles.css', 'script.js']
    
    print("\n📁 Checking frontend files...")
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    for file in required_files:
        file_path = frontend_dir / file
        if file_path.exists():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def check_ollama():
    """Check if Ollama is available"""
    print("\n🤖 Checking Ollama availability...")
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            return True
        else:
            print("⚠️  Ollama is running but returned unexpected response")
            return False
    except Exception as e:
        print("⚠️  Ollama not available - LLM features will be disabled")
        print("   To enable AI features, install and start Ollama:")
        print("   https://ollama.ai/")
        return False

def main():
    """Main startup function"""
    print("🚀 PII Processor Frontend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_and_install_requirements():
        print("\n❌ Dependency check failed. Please resolve and try again.")
        return 1
    
    # Check frontend files
    if not check_frontend_files():
        print("\n❌ Frontend files check failed. Please ensure all files are present.")
        return 1
    
    # Check Ollama (optional)
    ollama_available = check_ollama()
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! Starting server...")
    print("\n🌐 The frontend will be available at:")
    print("   http://localhost:5000")
    print("\n📝 Features available:")
    print("   ✅ Text anonymization/deanonymization")
    print("   ✅ File drag-and-drop (.txt files)")
    print("   ✅ Mapping file download/upload")
    print(f"   {'✅' if ollama_available else '⚠️ '} AI-powered entity detection")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and start the server
    try:
        from server import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False for cleaner output
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using PII Processor!")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 