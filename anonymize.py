import spacy

nlp = spacy.load("en_core_web_sm")

class Anonymizer:
    def __init__(self):
        self.doc = None
        # Counters for consistent anonymization
        self.entity_counters = {}
        # Custom mapping for more semantic labels
        self.label_mapping = {
            'PERSON': 'PERSON',
            'CARDINAL': 'NUMBER', 
            'FAC': 'ADDRESS',
            'GPE': 'LOCATION',
            'ORG': 'ORGANIZATION',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'MONEY': 'MONEY'
        }

    # def anonymize(self, data):
    #     self.data = data
    #     return self.data
    
    # def anonymize_column(self, column):
    #     return column.apply(self.anonymize_value)
    
    # def anonymize_value(self, value):
    #     return value

    def anonymize_data(self, file):
        self.doc = nlp(file)
        anonymized_doc = file
        
        # Reset counters for each document
        self.entity_counters = {}

        for ent in reversed(self.doc.ents):
            # Get the base label (use custom mapping if available)
            base_label = self.label_mapping.get(ent.label_, ent.label_)
            
            # Initialize counter for this label type if not exists
            if base_label not in self.entity_counters:
                self.entity_counters[base_label] = 0
            
            # Increment counter and create numbered placeholder
            self.entity_counters[base_label] += 1
            placeholder = f"[{base_label}{self.entity_counters[base_label]}]"
            
            # Replace in reverse order to maintain character positions
            anonymized_doc = anonymized_doc[:ent.start_char] + placeholder + anonymized_doc[ent.end_char:]
            
        return anonymized_doc


if __name__ == "__main__":
    anonymizer = Anonymizer()
    text = """My name is John Doe and I live in 123 Main St, Los Angeles, USA. 
    My daughter's name is Alice Doe and she lives in 456 Oak Avenue, New York City, USA."""
    anonymized_doc = anonymizer.anonymize_data(text)
    print(anonymized_doc)