#!/usr/bin/env python3
"""
Script to use the trained PII detection model for anonymization.
"""

import spacy
from pathlib import Path

class PIIAnonymizer:
    def __init__(self, model_path="./pii_model/model-best"):
        """Load the trained PII model."""
        try:
            self.nlp = spacy.load(model_path)
            print(f"✅ Loaded PII model from {model_path}")
            print(f"📝 Available labels: {list(self.nlp.get_pipe('ner').labels)}")
        except OSError:
            print(f"❌ Could not load model from {model_path}")
            print("💡 Make sure you've trained the model first!")
            raise
        
        # Counter for consistent anonymization
        self.entity_counters = {}
        
        # Mapping for cleaner labels
        self.label_mapping = {
            'PERSON': 'PERSON',
            'EMAIL': 'EMAIL', 
            'PHONE': 'PHONE',
            'SSN': 'SSN',
            'CREDIT_CARD': 'CREDIT_CARD',
            'ROUTING_NUMBER': 'ROUTING_NUMBER',
            'BANK_ACCOUNT': 'BANK_ACCOUNT',
            'ADDRESS': 'ADDRESS',
            'ZIP_CODE': 'ZIP',
            'DOB': 'DATE_OF_BIRTH',
            'RELATIONSHIP': 'RELATIONSHIP',
            'ORGANIZATION': 'ORGANIZATION',
            'JOB_TITLE': 'JOB_TITLE',
            'SALARY': 'SALARY',
            'PASSPORT': 'PASSPORT',
            'DRIVERS_LICENSE': 'DRIVERS_LICENSE',
            'MEDICAL_ID': 'MEDICAL_ID',
            'INSURANCE': 'INSURANCE',
            'EMPLOYEE_ID': 'EMPLOYEE_ID',
            'CUSTOMER_ID': 'CUSTOMER_ID',
            'AGE': 'AGE',
            'USERNAME': 'USERNAME',
            'MRN': 'MRN',
            'LOCATION': 'LOCATION',
            'MONEY': 'MONEY'
        }

    def anonymize_text(self, text, reset_counters=True):
        """Anonymize PII in the given text."""
        if reset_counters:
            self.entity_counters = {}
        
        # Process text with the model
        doc = self.nlp(text)
        
        # Collect entities and sort by position (reverse order for replacement)
        entities = []
        for ent in doc.ents:
            entities.append((ent.start_char, ent.end_char, ent.label_))
        
        # Sort by start position in reverse order to maintain character positions
        entities.sort(key=lambda x: x[0], reverse=True)
        
        anonymized_text = text
        
        for start, end, label in entities:
            # Get the base label (use custom mapping if available)
            base_label = self.label_mapping.get(label, label)
            
            # Initialize counter for this label type if not exists
            if base_label not in self.entity_counters:
                self.entity_counters[base_label] = 0
            
            # Increment counter and create numbered placeholder
            self.entity_counters[base_label] += 1
            placeholder = f"[{base_label}{self.entity_counters[base_label]}]"
            
            # Replace in reverse order to maintain character positions
            anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]
        
        return anonymized_text, entities

    def get_entities(self, text):
        """Extract entities without anonymizing."""
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': ent._.get('confidence', 'N/A')
            })
        return entities

    def demo(self):
        """Run a demo with sample text."""
        sample_texts = [
            "Contact Dr. Sarah Williams at sarah.w@hospital.com or (555) 123-4567. Her SSN is 123-45-6789.",
            "Employee John Smith (ID: EMP12345) earns $95,000 annually at Microsoft Corporation.",
            "My wife Jennifer lives at 123 Oak Street, Boston, MA 02101. Call her at 617-555-0199.",
            "Patient MRN: A12345, DOB: 03/15/1985, Insurance: INS789456, Age: 38 years old."
        ]
        
        print("\n" + "="*60)
        print("🔒 PII ANONYMIZATION DEMO")
        print("="*60)
        
        for i, text in enumerate(sample_texts, 1):
            print(f"\n📄 Example {i}:")
            print(f"Original: {text}")
            
            anonymized, entities = self.anonymize_text(text)
            print(f"Anonymized: {anonymized}")
            
            if entities:
                print("🏷️  Detected entities:")
                for start, end, label in sorted(entities):
                    entity_text = text[start:end]
                    print(f"   • {entity_text} → {label}")
            else:
                print("🏷️  No entities detected")

def main():
    """Main function to demonstrate usage."""
    # Check if model exists
    model_path = Path("./pii_model/model-best")
    if not model_path.exists():
        print("❌ Model not found! Train the model first:")
        print("python -m spacy train configs/pii_ner_simple.cfg --paths.train train.spacy --paths.dev dev.spacy --output ./pii_model")
        return
    
    # Initialize anonymizer
    anonymizer = PIIAnonymizer()
    
    # Run demo
    anonymizer.demo()
    
    # Interactive mode
    print("\n" + "="*60)
    print("🔄 INTERACTIVE MODE")
    print("="*60)
    print("Enter text to anonymize (or 'quit' to exit):")
    
    while True:
        text = input("\n📝 Input: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not text:
            continue
        
        try:
            anonymized, entities = anonymizer.anonymize_text(text)
            print(f"🔒 Anonymized: {anonymized}")
            
            if entities:
                print("🏷️  Detected:")
                for start, end, label in sorted(entities):
                    entity_text = text[start:end]
                    print(f"   • {entity_text} → {label}")
        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 