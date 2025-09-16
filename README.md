# PII Anonymizer

A comprehensive, secure solution for anonymizing and deanonymizing Personally Identifiable Information (PII) in documents. This tool uses AI-powered entity detection and deterministic placeholders to safely process sensitive documents while maintaining the ability to restore original data.

![PII Anonymizer Demo](https://img.shields.io/badge/Version-1.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.12%2B-brightgreen) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/PII_Anonymizer.git
cd PII_Anonymizer

# Install dependencies
pip install -r requirements.txt

# Start the web interface
python start_frontend.py
```

Open your browser to `http://localhost:5000` and start anonymizing documents!

## ✨ Features

### 🔒 **Anonymization**
- **AI-powered detection** using Ollama for context-aware entity recognition
- **Regex-based detection** for precise pattern matching (emails, SSNs, etc.)
- **Deterministic placeholders** (`[PERSON1]`, `[DATE1]`, `[PHONE1]`)
- **Multiple input formats** (text, .txt files, planned: PDF, Excel, Word)
- **Preservation of document structure** and formatting

### 🔓 **Deanonymization**
- **Complete restoration** of original text using mapping files
- **Batch processing** of multiple documents
- **Mapping validation** and error handling
- **JSON-based mapping files** for easy storage and transfer

### 🌐 **Web Interface**
- **Modern, responsive design** for all devices
- **Drag-and-drop file support** with visual feedback
- **Real-time processing** with progress indicators
- **Copy/download functionality** for results
- **Dual-mode interface** (anonymize/deanonymize)

### 🛡️ **Security & Privacy**
- **Local processing** - data never leaves your environment
- **No cloud dependencies** for core functionality
- **Secure file handling** with automatic cleanup
- **Configurable salt** for deterministic generation
- **No logging** of sensitive content

## 📋 Requirements

### System Requirements
- **Python 3.12 or higher**
- **4GB RAM minimum** (8GB+ recommended for large documents)
- **1GB disk space** for installation and temporary files
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Optional for Enhanced Features
- **Ollama** for AI-powered entity detection
  - Improves accuracy for names, organizations, locations
  - Supports multiple languages and contexts
  - Download from: https://ollama.ai/

## 🔧 Installation

### Option 1: Automatic Installation (Recommended)

The startup script will automatically check and install dependencies:

```bash
git clone https://github.com/yourusername/PII_Anonymizer.git
cd PII_Anonymizer
python start_frontend.py
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/PII_Anonymizer.git
cd PII_Anonymizer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (optional, for AI features)
# Visit https://ollama.ai/ for installation instructions

# Download an AI model (if using Ollama)
ollama pull llama3.2:3b
```

### Option 3: Development Installation

For development or customization:

```bash
git clone https://github.com/yourusername/PII_Anonymizer.git
cd PII_Anonymizer

# Install in development mode
pip install -e .

# Install additional development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black .
```

## 🎯 Usage

### Web Interface (Recommended)

1. **Start the server:**
   ```bash
   python start_frontend.py
   ```

2. **Open browser:** Navigate to `http://localhost:5000`

3. **Anonymize documents:**
   - Switch to "Anonymize" mode
   - Drag .txt files or paste text directly
   - Configure AI detection (requires Ollama)
   - Click "Anonymize"
   - Download mapping file for later restoration

4. **Deanonymize documents:**
   - Switch to "Deanonymize" mode
   - Paste anonymized text
   - Upload or paste mapping JSON
   - Click "Deanonymize"
   - Copy restored results

### Command Line Interface

#### Basic Anonymization
```python
from pii_processor import quick_anonymize, quick_deanonymize

# Anonymize text
text = "Contact John Doe at john.doe@email.com or call (555) 123-4567."
anonymized, mapping = quick_anonymize(text, use_llm=True)

print("Anonymized:", anonymized)
# Output: Contact [PERSON1] at [EMAIL1] or call [PHONE1].

print("Mapping:", mapping)
# Output: {'John Doe': '[PERSON1]', 'john.doe@email.com': '[EMAIL1]', ...}
```

#### Complete Workflow
```python
from pii_processor import PIIProcessor

# Initialize processor
processor = PIIProcessor(use_llm=True)

# Process sensitive document
original_text = "Patient John Smith (SSN: 123-45-6789) scheduled for 2024-01-15."

# Anonymize
anonymized_text, mapping = processor.anonymize_text(
    original_text, 
    save_mapping_to="patient_mapping.json"
)

# Simulate sending to external service
external_response = f"Scheduling confirmed for {anonymized_text}"

# Restore original information
final_response = processor.deanonymize_text(
    external_response, 
    mapping_file="patient_mapping.json"
)
```

#### Batch Processing
```python
import os
from pathlib import Path

processor = PIIProcessor(use_llm=True)

# Process multiple files
input_dir = Path("sensitive_documents")
output_dir = Path("anonymized_documents")
mapping_dir = Path("mappings")

for txt_file in input_dir.glob("*.txt"):
    # Read file
    content = txt_file.read_text()
    
    # Anonymize
    anonymized, mapping = processor.anonymize_text(
        content,
        save_mapping_to=mapping_dir / f"{txt_file.stem}_mapping.json"
    )
    
    # Save anonymized version
    output_file = output_dir / f"{txt_file.stem}_anonymized.txt"
    output_file.write_text(anonymized)
    
    print(f"Processed: {txt_file.name}")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Security
PII_SECRET_SALT=your-custom-salt-here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# File Processing
MAX_FILE_SIZE_MB=16
TEMP_DIR=/tmp/pii_processor

# Logging
LOG_LEVEL=INFO
LOG_FILE=pii_processor.log
```

### Custom Salt Configuration

For production use, change the default salt:

```python
# In anonymize.py, update:
SECRET_SALT = b"your-custom-salt-here"

# Or use environment variable:
import os
SECRET_SALT = os.environ.get('PII_SECRET_SALT', 'default-salt').encode()
```

### Ollama Model Selection

Configure different models for different use cases:

```python
# High accuracy (slower)
processor = PIIProcessor(use_llm=True)
# Uses default model (llama3.2:3b)

# Fast processing (lower accuracy)
# Modify anonymize.py to use a smaller model
# model="qwen2.5:1.5b-instruct"
```

## 📁 File Format Support

### Currently Supported
- ✅ **Plain text (.txt)** - Full support
- ✅ **JSON mapping files (.json)** - Full support
- ✅ **Direct text input** - Copy/paste functionality

### Planned Support
- 🚧 **PDF files (.pdf)** - Text extraction ready
- 🚧 **Excel files (.xlsx)** - Data extraction planned
- 🚧 **Word documents (.docx)** - Text extraction planned
- 🚧 **CSV files (.csv)** - Structured data processing

### Adding File Format Support

To add support for new file formats:

1. **Update the frontend** (`frontend/script.js`):
   ```javascript
   // Add to extractTextFromFile method
   case '.pdf':
       return this.extractFromPDF(file);
   ```

2. **Implement extraction** in the backend (`server.py`):
   ```python
   def extract_pdf_text(file_path):
       import PyPDF2
       # Implementation here
       return extracted_text
   ```

3. **Update file validation** in both frontend and backend

## 🚀 API Reference

### REST API Endpoints

#### `POST /api/anonymize`
Anonymize text content.

**Request:**
```json
{
    "text": "Contact John Doe at john@email.com",
    "use_llm": true
}
```

**Response:**
```json
{
    "success": true,
    "anonymized_text": "Contact [PERSON1] at [EMAIL1]",
    "mapping": {"John Doe": "[PERSON1]", "john@email.com": "[EMAIL1]"},
    "spans": [{"start": 8, "end": 16, "label": "PERSON"}]
}
```

#### `POST /api/deanonymize`
Restore original text from anonymized content.

**Request:**
```json
{
    "anonymized_text": "Contact [PERSON1] at [EMAIL1]",
    "mapping": {"John Doe": "[PERSON1]", "john@email.com": "[EMAIL1]"}
}
```

**Response:**
```json
{
    "success": true,
    "restored_text": "Contact John Doe at john@email.com"
}
```

#### `POST /api/upload`
Upload and process files.

**Request:** Multipart form data with file

**Response:**
```json
{
    "success": true,
    "text": "Extracted file content...",
    "filename": "document.txt"
}
```

#### `GET /api/health`
Check system health and availability.

**Response:**
```json
{
    "success": true,
    "status": "healthy",
    "ollama_available": true
}
```

## 🛠️ Development

### Project Structure
```
PII_Anonymizer/
├── frontend/              # Web interface
│   ├── index.html         # Main UI
│   ├── styles.css         # Styling
│   └── script.js          # Frontend logic
├── anonymize.py           # Core anonymization
├── deanonymize.py         # Core deanonymization
├── pii_processor.py       # Unified API
├── server.py              # Flask backend
├── start_frontend.py      # Easy startup
├── requirements.txt       # Dependencies
├── .gitignore            # Git exclusions
└── README.md             # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest test_anonymization.py::test_email_detection
```

### Code Quality

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Security scan
bandit -r .
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format code (`black .`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

#### "Ollama not available"
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download a model
ollama pull llama3.2:3b
```

#### "Flask dependencies missing"
```bash
# Install missing packages
pip install Flask Flask-CORS requests

# Or install all requirements
pip install -r requirements.txt
```

#### "Permission denied" errors
```bash
# Fix file permissions
chmod +x start_frontend.py

# Or run with Python
python start_frontend.py
```

#### "Port 5000 already in use"
```bash
# Kill process using port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or use a different port
export FLASK_PORT=5001
python start_frontend.py
```

#### Memory issues with large files
- Increase system RAM or use virtual memory
- Process files in smaller chunks
- Use regex-only mode instead of LLM for faster processing

### Debug Mode

Enable debug mode for development:

```python
# In start_frontend.py, set:
app.run(debug=True)

# Or use environment variable:
export FLASK_DEBUG=1
python server.py
```

### Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance

### Benchmarks
- **Small documents** (< 1KB): ~50ms processing time
- **Medium documents** (1-100KB): ~200ms processing time  
- **Large documents** (100KB-1MB): ~2-5s processing time
- **Memory usage**: ~100-500MB depending on document size

### Optimization Tips
- Use regex-only mode for faster processing
- Disable LLM for simple PII patterns
- Process files in batches for better throughput
- Use SSD storage for temporary files

## 🔒 Security Considerations

### Data Handling
- All processing occurs locally
- Temporary files are automatically cleaned
- No network transmission of sensitive data
- Configurable salt for deterministic generation

### Production Deployment
```bash
# Use environment variables for secrets
export PII_SECRET_SALT="your-production-salt"

# Run with production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# Set up reverse proxy (nginx)
# Configure HTTPS certificates
# Enable firewall rules
```

### Security Best Practices
- Change default salt in production
- Use HTTPS for web deployment
- Regularly update dependencies
- Monitor access logs
- Implement rate limiting for API endpoints

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for providing local LLM capabilities
- **Flask** for the web framework
- **Font Awesome** for icons
- **The open source community** for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/PII_Anonymizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/PII_Anonymizer/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/PII_Anonymizer/wiki)

---

**Made with ❤️ for privacy and security**
