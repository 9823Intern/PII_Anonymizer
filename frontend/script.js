// PII Processor Frontend JavaScript
class PIIProcessor {
    constructor() {
        this.currentMode = 'anonymize';
        this.currentMapping = null;
        this.initializeEventListeners();
        this.initializeDragAndDrop();
    }

    initializeEventListeners() {
        // Mode switching
        document.getElementById('anonymize-btn').addEventListener('click', () => this.switchMode('anonymize'));
        document.getElementById('deanonymize-btn').addEventListener('click', () => this.switchMode('deanonymize'));

        // Process buttons
        document.getElementById('anonymize-process-btn').addEventListener('click', () => this.processAnonymize());
        document.getElementById('deanonymize-process-btn').addEventListener('click', () => this.processDeanonymize());

        // Copy buttons
        document.getElementById('copy-anonymized').addEventListener('click', () => this.copyToClipboard('anonymized-output'));
        document.getElementById('copy-restored').addEventListener('click', () => this.copyToClipboard('restored-output'));

        // Download button
        document.getElementById('download-mapping').addEventListener('click', () => this.downloadMapping());

        // Browse links
        document.querySelectorAll('.browse-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const dropzone = e.target.closest('.dropzone');
                const fileInput = dropzone.querySelector('input[type="file"]');
                fileInput.click();
            });
        });

        // File input changes
        document.getElementById('anonymize-file-input').addEventListener('change', (e) => this.handleFileSelect(e, 'anonymize'));
        document.getElementById('deanonymize-file-input').addEventListener('change', (e) => this.handleFileSelect(e, 'deanonymize'));
        document.getElementById('mapping-file-input').addEventListener('change', (e) => this.handleMappingFileSelect(e));
    }

    initializeDragAndDrop() {
        // Anonymize dropzone
        this.setupDropzone('anonymize-dropzone', 'anonymize-file-input', (file) => this.processFile(file, 'anonymize'));
        
        // Deanonymize dropzone
        this.setupDropzone('deanonymize-dropzone', 'deanonymize-file-input', (file) => this.processFile(file, 'deanonymize'));
        
        // Mapping dropzone
        this.setupDropzone('mapping-dropzone', 'mapping-file-input', (file) => this.processMappingFile(file));
    }

    setupDropzone(dropzoneId, inputId, callback) {
        const dropzone = document.getElementById(dropzoneId);
        const input = document.getElementById(inputId);

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
        });

        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                callback(files[0]);
                input.files = files;
            }
        });

        dropzone.addEventListener('click', () => input.click());
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${mode}-btn`).classList.add('active');
        
        // Update content visibility
        document.querySelectorAll('.mode-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${mode}-mode`).classList.add('active');
        
        this.updateStatus(`Switched to ${mode} mode`);
    }

    async processFile(file, mode) {
        if (!this.validateFile(file, mode)) return;

        const text = await this.extractTextFromFile(file);
        if (text) {
            const textArea = document.getElementById(`${mode}-text-input`);
            textArea.value = text;
            this.updateDropzoneState(file.name, mode);
        }
    }

    async processMappingFile(file) {
        if (!file.name.endsWith('.json')) {
            this.showError('Please select a JSON file for the mapping');
            return;
        }

        try {
            const text = await file.text();
            const mapping = JSON.parse(text);
            document.getElementById('mapping-text-input').value = JSON.stringify(mapping, null, 2);
            this.currentMapping = mapping;
            this.updateDropzoneState(file.name, 'mapping');
            this.updateStatus('Mapping file loaded successfully');
        } catch (error) {
            this.showError('Invalid JSON file. Please check the format.');
            console.error('Mapping file error:', error);
        }
    }

    validateFile(file, mode) {
        const allowedTypes = ['.txt', '.pdf', '.xlsx', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            this.showError(`Unsupported file type: ${fileExtension}. Supported types: ${allowedTypes.join(', ')}`);
            return false;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.showError('File size too large. Please select a file smaller than 10MB.');
            return false;
        }
        
        return true;
    }

    async extractTextFromFile(file) {
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        try {
            switch (fileExtension) {
                case '.txt':
                    return await file.text();
                case '.pdf':
                    return this.extractFromPDF(file);
                case '.xlsx':
                    return this.extractFromExcel(file);
                case '.docx':
                    return this.extractFromWord(file);
                default:
                    throw new Error('Unsupported file type');
            }
        } catch (error) {
            this.showError(`Error reading file: ${error.message}`);
            return null;
        }
    }

    // Placeholder functions for file processing (you'll implement these later)
    async extractFromPDF(file) {
        // TODO: Implement PDF text extraction
        this.showError('PDF processing not yet implemented. Please convert to .txt for now.');
        return null;
    }

    async extractFromExcel(file) {
        // TODO: Implement Excel text extraction
        this.showError('Excel processing not yet implemented. Please convert to .txt for now.');
        return null;
    }

    async extractFromWord(file) {
        // TODO: Implement Word text extraction
        this.showError('Word document processing not yet implemented. Please convert to .txt for now.');
        return null;
    }

    updateDropzoneState(filename, type) {
        const dropzoneId = type === 'mapping' ? 'mapping-dropzone' : `${type}-dropzone`;
        const dropzone = document.getElementById(dropzoneId);
        
        dropzone.classList.add('file-uploaded');
        const content = dropzone.querySelector('.dropzone-content');
        content.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <p><strong>${filename}</strong></p>
            <p class="file-types">File loaded successfully</p>
        `;
    }

    async processAnonymize() {
        const text = document.getElementById('anonymize-text-input').value.trim();
        const useLLM = document.getElementById('use-llm').checked;

        if (!text) {
            this.showError('Please provide text to anonymize');
            return;
        }

        this.setProcessing(true);
        this.updateStatus('Anonymizing text...');

        try {
            // Call the Python backend
            const response = await fetch('/api/anonymize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    use_llm: useLLM
                })
            });

            if (!response.ok) {
                throw new Error('Failed to anonymize text');
            }

            const result = await response.json();
            
            // Update output areas
            document.getElementById('anonymized-output').value = result.anonymized_text;
            document.getElementById('mapping-output').value = JSON.stringify(result.mapping, null, 2);
            
            this.currentMapping = result.mapping;
            this.updateStatus('Text anonymized successfully');
            
        } catch (error) {
            this.showError('Error anonymizing text. Make sure the backend server is running.');
            console.error('Anonymization error:', error);
        } finally {
            this.setProcessing(false);
        }
    }

    async processDeanonymize() {
        const anonymizedText = document.getElementById('deanonymize-text-input').value.trim();
        const mappingText = document.getElementById('mapping-text-input').value.trim();

        if (!anonymizedText) {
            this.showError('Please provide anonymized text');
            return;
        }

        if (!mappingText) {
            this.showError('Please provide a mapping JSON');
            return;
        }

        let mapping;
        try {
            mapping = JSON.parse(mappingText);
        } catch (error) {
            this.showError('Invalid mapping JSON format');
            return;
        }

        this.setProcessing(true);
        this.updateStatus('Deanonymizing text...');

        try {
            // Call the Python backend
            const response = await fetch('/api/deanonymize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    anonymized_text: anonymizedText,
                    mapping: mapping
                })
            });

            if (!response.ok) {
                throw new Error('Failed to deanonymize text');
            }

            const result = await response.json();
            
            // Update output area
            document.getElementById('restored-output').value = result.restored_text;
            this.updateStatus('Text deanonymized successfully');
            
        } catch (error) {
            this.showError('Error deanonymizing text. Make sure the backend server is running.');
            console.error('Deanonymization error:', error);
        } finally {
            this.setProcessing(false);
        }
    }

    handleFileSelect(event, mode) {
        const file = event.target.files[0];
        if (file) {
            this.processFile(file, mode);
        }
    }

    handleMappingFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.processMappingFile(file);
        }
    }

    async copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const text = element.value;

        if (!text) {
            this.showError('Nothing to copy');
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            this.updateStatus('Copied to clipboard');
            
            // Visual feedback
            const button = event.target.closest('button');
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            
            setTimeout(() => {
                button.innerHTML = originalIcon;
            }, 1000);
            
        } catch (error) {
            this.showError('Failed to copy to clipboard');
        }
    }

    downloadMapping() {
        if (!this.currentMapping) {
            this.showError('No mapping available to download');
            return;
        }

        const blob = new Blob([JSON.stringify(this.currentMapping, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pii_mapping_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.updateStatus('Mapping file downloaded');
    }

    setProcessing(isProcessing) {
        const indicator = document.getElementById('processing-indicator');
        const buttons = document.querySelectorAll('.process-btn');
        
        if (isProcessing) {
            indicator.classList.remove('hidden');
            buttons.forEach(btn => btn.disabled = true);
        } else {
            indicator.classList.add('hidden');
            buttons.forEach(btn => btn.disabled = false);
        }
    }

    updateStatus(message) {
        document.getElementById('status-message').textContent = message;
        
        // Clear the message after 5 seconds
        setTimeout(() => {
            document.getElementById('status-message').textContent = 'Ready';
        }, 5000);
    }

    showError(message) {
        this.updateStatus(`Error: ${message}`);
        document.getElementById('status-message').style.color = 'var(--danger-color)';
        
        setTimeout(() => {
            document.getElementById('status-message').style.color = '';
        }, 5000);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PIIProcessor();
});

// Service worker registration for offline capability (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered: ', registration))
            .catch(registrationError => console.log('SW registration failed: ', registrationError));
    });
} 