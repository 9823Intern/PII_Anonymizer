import json
import re
from typing import Dict, Tuple

def deanonymize(anonymized_text: str, mapping: Dict[str, str]) -> str:
    """
    Reverse the anonymization process by replacing placeholders with original values.
    
    Args:
        anonymized_text: Text with placeholders like [PERSON1], [DATE1], etc.
        mapping: Dictionary mapping original text to placeholders (from anonymize.py)
    
    Returns:
        Text with placeholders replaced by original values
    """
    # Create reverse mapping: placeholder -> original text
    reverse_mapping = {placeholder: original for original, placeholder in mapping.items()}
    
    # Find all placeholders in the text
    placeholder_pattern = r'\[[A-Z]+\d+\]'
    placeholders = re.findall(placeholder_pattern, anonymized_text)
    
    # Replace each placeholder with its original value
    result = anonymized_text
    for placeholder in placeholders:
        if placeholder in reverse_mapping:
            original_value = reverse_mapping[placeholder]
            result = result.replace(placeholder, original_value)
        else:
            print(f"Warning: No mapping found for placeholder: {placeholder}")
    
    return result

def deanonymize_from_files(anonymized_text: str, mapping_file: str) -> str:
    """
    Deanonymize text using a mapping from a JSON file.
    
    Args:
        anonymized_text: Text with placeholders
        mapping_file: Path to JSON file containing the mapping dictionary
    
    Returns:
        Deanonymized text
    """
    try:
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        return deanonymize(anonymized_text, mapping)
    except FileNotFoundError:
        print(f"Error: Mapping file {mapping_file} not found")
        return anonymized_text
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in mapping file {mapping_file}")
        return anonymized_text

def save_mapping(mapping: Dict[str, str], filename: str) -> None:
    """
    Save the mapping dictionary to a JSON file for later use.
    
    Args:
        mapping: The mapping dictionary from anonymize.py
        filename: Path where to save the JSON file
    """
    with open(filename, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Mapping saved to {filename}")

def load_mapping(filename: str) -> Dict[str, str]:
    """
    Load a mapping dictionary from a JSON file.
    
    Args:
        filename: Path to the JSON mapping file
    
    Returns:
        The mapping dictionary
    """
    with open(filename, 'r') as f:
        return json.load(f)

# Example usage and testing
if __name__ == "__main__":
    # Example mapping (this would normally come from anonymize.py)
    example_mapping = {
        'John A. Doe': '[PERSON1]',
        '07/22/1986': '[DATE1]', 
        '123-45-6789': '[SSN1]',
        'Globex LLC': '[ORG1]',
        '742 Evergreen Terrace, Apt. 4B, Springfield, IL 62704': '[LOCATION1]',
        '(415) 555-2672': '[PHONE1]',
        'john.doe@example.test': '[EMAIL1]'
    }
    
    # Example anonymized text
    anonymized_sample = """
Plaintiff [PERSON1], born July 22, 1986 (DOB: [DATE1]; SSN: [SSN1]), brings this action against 
Defendant [ORG1] for breach of an employment agreement and for related declaratory and injunctive relief. Mr. Doe 
is a long-time resident at [LOCATION1] (telephone: [PHONE1]; email: [EMAIL1])
    """
    
    print("=== Deanonymization Test ===")
    print("Original anonymized text:")
    print(anonymized_sample)
    print("\nMapping:")
    print(json.dumps(example_mapping, indent=2))
    
    # Deanonymize
    restored_text = deanonymize(anonymized_sample, example_mapping)
    print("\nDeanonymized text:")
    print(restored_text)
    
    # Test file save/load
    print("\n=== File Operations Test ===")
    save_mapping(example_mapping, "test_mapping.json")
    
    # Test loading and deanonymizing from file
    restored_from_file = deanonymize_from_files(anonymized_sample, "test_mapping.json")
    print("Deanonymized from file:")
    print(restored_from_file)
