# PII Processor Frontend

A modern web interface for secure anonymization and deanonymization of sensitive documents.

## 🚀 Quick Start

1. **Start the frontend server:**
   ```bash
   python start_frontend.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Start processing documents!**

## ✨ Features

### 🔒 Anonymize Mode
- **Drag & drop files** or paste text directly
- **AI-powered entity detection** (requires Ollama)
- **Multiple file formats** (planned: .txt, .pdf, .xlsx, .docx)
- **Download mapping files** for later deanonymization
- **Copy results** to clipboard with one click

### 🔓 Deanonymize Mode  
- **Restore original text** using mapping files
- **Drag & drop mapping files** or paste JSON directly
- **Bulk processing** of anonymized documents
- **Seamless workflow** integration

### 🛠️ Technical Features
- **Responsive design** - works on desktop, tablet, and mobile
- **Real-time processing** with visual feedback
- **Error handling** with helpful messages
- **File validation** and size limits
- **Secure processing** - files processed locally

## 📁 File Support

### Currently Supported
- **Text files (.txt)** - Full support
- **JSON mapping files (.json)** - Full support

### Planned Support (Placeholders Ready)
- **PDF files (.pdf)** - Text extraction
- **Excel files (.xlsx)** - Content extraction  
- **Word documents (.docx)** - Text extraction

## 🤖 AI Features

The frontend integrates with **Ollama** for enhanced entity detection:

- **Better accuracy** for names, locations, organizations
- **Context-aware** detection
- **Multilingual support** (model dependent)

**To enable AI features:**
1. Install Ollama: https://ollama.ai/
2. Download a model: `ollama pull llama3.2:3b`
3. Restart the frontend

## 🔧 API Endpoints

The frontend communicates with these backend endpoints:

- `POST /api/anonymize` - Anonymize text
- `POST /api/deanonymize` - Restore text
- `POST /api/upload` - Process file uploads
- `GET /api/health` - Check system status

## 🎨 User Interface

### Layout
- **Dual-panel design** for input and output
- **Mode switching** between anonymize/deanonymize
- **Status indicators** for all operations
- **Progress feedback** during processing

### Drag & Drop Zones
- **Visual feedback** when dragging files
- **File type validation** with helpful messages
- **Multiple drop zones** for different file types
- **Success/error states** with clear indicators

### Output Management
- **Copy to clipboard** functionality
- **Download mapping files** for safekeeping
- **Formatted JSON** display for mappings
- **Text formatting** preservation

## 🔒 Security & Privacy

- **Local processing** - sensitive data never leaves your environment
- **Temporary files** are automatically cleaned up
- **No logging** of sensitive content
- **Secure file handling** with validation
- **HTTPS ready** for production deployment

## 🛠️ Development

### File Structure
```
PII_Anonymizer/
├── frontend/
│   ├── index.html      # Main interface
│   ├── styles.css      # Modern styling
│   └── script.js       # Interactive functionality
├── server.py           # Flask backend
├── start_frontend.py   # Easy startup script
└── requirements.txt    # Dependencies
```

### Dependencies
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin support
- **Requests** - HTTP client

### Customization
The frontend is built with modern web standards and can be easily customized:

- **CSS variables** for theming
- **Modular JavaScript** classes
- **Responsive breakpoints** for mobile
- **Icon system** with Font Awesome

## 🐛 Troubleshooting

### Common Issues

**"Backend server not running"**
- Ensure Python dependencies are installed
- Check that port 5000 is available
- Verify all files are in the correct directory

**"Ollama not available"**
- Install Ollama from https://ollama.ai/
- Start Ollama service
- Download a compatible model

**"File processing failed"**
- Check file format is supported
- Verify file size is under 16MB
- Ensure file is not corrupted

### Getting Help
- Check the browser console for JavaScript errors
- Review server logs for backend issues
- Verify file permissions and paths

## 🚀 Production Deployment

For production use:

1. **Set Flask environment:**
   ```bash
   export FLASK_ENV=production
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 server:app
   ```

3. **Configure reverse proxy** (nginx/Apache)
4. **Enable HTTPS** for secure communication
5. **Set up monitoring** and logging

## 📄 License

This project is part of the PII Anonymizer suite and follows the same licensing terms. 