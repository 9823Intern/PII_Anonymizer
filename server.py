#!/usr/bin/env python3
"""
Flask Backend Server for PII Processor Frontend

This server provides:
1. Static file serving for the frontend
2. API endpoints for anonymization and deanonymization
3. File upload handling
4. Integration with the existing PII processing modules
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import json
import tempfile
from pathlib import Path

# Import our PII processing modules
from pii_processor import PIIProcessor, quick_anonymize, quick_deanonymize
from anonymize import anonymize
from deanonymize import deanonymize

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize PII processor
pii_processor = PIIProcessor(use_llm=True)

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the frontend directory"""
    return send_from_directory('frontend', filename)

@app.route('/api/anonymize', methods=['POST'])
def api_anonymize():
    """
    Anonymize text via API
    
    Expected JSON payload:
    {
        "text": "Text to anonymize",
        "use_llm": true/false
    }
    
    Returns:
    {
        "anonymized_text": "Text with [PERSON1] placeholders",
        "mapping": {"Original": "[PLACEHOLDER1]", ...},
        "spans": [...],
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False, 
                'error': 'Missing text parameter'
            }), 400
        
        text = data['text']
        use_llm = data.get('use_llm', True)
        
        if not text.strip():
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        # Process the text
        anonymized_text, mapping, spans = anonymize(text, use_llm=use_llm)
        
        return jsonify({
            'success': True,
            'anonymized_text': anonymized_text,
            'mapping': mapping,
            'spans': [{'start': s.start, 'end': s.end, 'label': s.label} for s in spans]
        })
        
    except Exception as e:
        app.logger.error(f"Anonymization error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/deanonymize', methods=['POST'])
def api_deanonymize():
    """
    Deanonymize text via API
    
    Expected JSON payload:
    {
        "anonymized_text": "Text with [PERSON1] placeholders",
        "mapping": {"Original": "[PLACEHOLDER1]", ...}
    }
    
    Returns:
    {
        "restored_text": "Text with original PII restored",
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'anonymized_text' not in data or 'mapping' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing anonymized_text or mapping parameter'
            }), 400
        
        anonymized_text = data['anonymized_text']
        mapping = data['mapping']
        
        if not anonymized_text.strip():
            return jsonify({
                'success': False,
                'error': 'Anonymized text cannot be empty'
            }), 400
        
        if not isinstance(mapping, dict):
            return jsonify({
                'success': False,
                'error': 'Mapping must be a dictionary'
            }), 400
        
        # Process the text
        restored_text = deanonymize(anonymized_text, mapping)
        
        return jsonify({
            'success': True,
            'restored_text': restored_text
        })
        
    except Exception as e:
        app.logger.error(f"Deanonymization error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    Handle file uploads and extract text
    
    Expected: multipart/form-data with 'file' field
    Optional: 'mode' field ('anonymize' or 'deanonymize')
    
    Returns:
    {
        "text": "Extracted text content",
        "filename": "original_filename.ext",
        "success": true
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        mode = request.form.get('mode', 'anonymize')
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'.txt', '.pdf', '.xlsx', '.docx', '.json'}
        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_ext}'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text based on file type
            if file_ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_ext == '.json':
                # Handle JSON mapping files
                with open(filepath, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                return jsonify({
                    'success': True,
                    'mapping': mapping_data,
                    'filename': file.filename
                })
            else:
                # For PDF, Excel, Word - placeholder implementation
                text = f"[File processing for {file_ext} not yet implemented. Please convert to .txt format.]"
            
            return jsonify({
                'success': True,
                'text': text,
                'filename': file.filename
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload processing error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'ollama_available': check_ollama_availability()
    })

def check_ollama_availability():
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        return response.status_code == 200
    except:
        return False

def secure_filename(filename):
    """
    Secure a filename by removing potentially dangerous characters
    Simple implementation - in production, use werkzeug.utils.secure_filename
    """
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving the main page (SPA routing)"""
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    # Ensure frontend directory exists
    frontend_dir = Path(__file__).parent / 'frontend'
    if not frontend_dir.exists():
        print("Error: frontend directory not found!")
        print("Make sure the frontend files are in the 'frontend' subdirectory.")
        exit(1)
    
    print("🚀 Starting PII Processor Server...")
    print("📁 Frontend files:", frontend_dir.absolute())
    print("🤖 Ollama available:", check_ollama_availability())
    print("🌐 Open http://localhost:5000 in your browser")
    print("📝 API endpoints:")
    print("   POST /api/anonymize - Anonymize text")
    print("   POST /api/deanonymize - Deanonymize text")
    print("   POST /api/upload - Upload and process files")
    print("   GET /api/health - Health check")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 