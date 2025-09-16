#!/usr/bin/env python3
"""
PII Processor - Unified API for anonymization and deanonymization

This module provides a simple interface for processing sensitive documents
with PII anonymization and deanonymization capabilities.
"""

import json
import tempfile
import os
from typing import Tuple, Dict, Optional
from pathlib import Path

from anonymize import anonymize
from deanonymize import deanonymize, save_mapping, load_mapping

class PIIProcessor:
    """
    A class to handle PII anonymization and deanonymization workflows.
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the PII processor.
        
        Args:
            use_llm: Whether to use LLM for entity detection (more accurate but requires Ollama)
        """
        self.use_llm = use_llm
        self.current_mapping: Optional[Dict[str, str]] = None
        self.mapping_file: Optional[str] = None
    
    def anonymize_text(self, text: str, save_mapping_to: Optional[str] = None) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize text by replacing PII with placeholders.
        
        Args:
            text: The original text containing PII
            save_mapping_to: Optional filename to save the mapping for later deanonymization
        
        Returns:
            Tuple of (anonymized_text, mapping_dictionary)
        """
        anonymized_text, mapping, spans = anonymize(text, use_llm=self.use_llm)
        
        # Store mapping for this session
        self.current_mapping = mapping
        
        # Save mapping to file if requested
        if save_mapping_to:
            save_mapping(mapping, save_mapping_to)
            self.mapping_file = save_mapping_to
        
        return anonymized_text, mapping
    
    def deanonymize_text(self, anonymized_text: str, mapping: Optional[Dict[str, str]] = None, 
                        mapping_file: Optional[str] = None) -> str:
        """
        Deanonymize text by replacing placeholders with original PII.
        
        Args:
            anonymized_text: Text containing placeholders like [PERSON1], [DATE1], etc.
            mapping: Mapping dictionary (if not provided, uses current session mapping)
            mapping_file: Path to mapping file (alternative to mapping dict)
        
        Returns:
            Text with placeholders replaced by original PII
        """
        # Determine which mapping to use
        if mapping:
            use_mapping = mapping
        elif mapping_file:
            use_mapping = load_mapping(mapping_file)
        elif self.current_mapping:
            use_mapping = self.current_mapping
        elif self.mapping_file:
            use_mapping = load_mapping(self.mapping_file)
        else:
            raise ValueError("No mapping provided. Please provide mapping dict, mapping file, or run anonymize_text first.")
        
        return deanonymize(anonymized_text, use_mapping)
    
    def process_web_llm_workflow(self, original_text: str, web_llm_response: str, 
                                mapping_file: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Complete workflow for using web LLMs safely with PII.
        
        Args:
            original_text: Original text with PII
            web_llm_response: Response from web LLM (containing anonymized placeholders)
            mapping_file: Optional file to save/load mapping
        
        Returns:
            Tuple of (anonymized_input, deanonymized_response, mapping_file_used)
        """
        # Step 1: Anonymize the original text
        if not mapping_file:
            mapping_file = tempfile.mktemp(suffix=".json", prefix="pii_mapping_")
        
        anonymized_input, mapping = self.anonymize_text(original_text, mapping_file)
        
        # Step 2: Deanonymize the web LLM response
        deanonymized_response = self.deanonymize_text(web_llm_response, mapping_file=mapping_file)
        
        return anonymized_input, deanonymized_response, mapping_file
    
    def cleanup_mapping_file(self):
        """Remove the current mapping file."""
        if self.mapping_file and os.path.exists(self.mapping_file):
            os.remove(self.mapping_file)
            self.mapping_file = None

# Convenience functions for simple use cases
def quick_anonymize(text: str, use_llm: bool = True) -> Tuple[str, Dict[str, str]]:
    """Quick anonymization without creating a processor instance."""
    processor = PIIProcessor(use_llm=use_llm)
    return processor.anonymize_text(text)

def quick_deanonymize(anonymized_text: str, mapping: Dict[str, str]) -> str:
    """Quick deanonymization without creating a processor instance."""
    processor = PIIProcessor()
    return processor.deanonymize_text(anonymized_text, mapping)

# Example usage
if __name__ == "__main__":
    # Example 1: Simple anonymization/deanonymization
    print("=== Simple Example ===")
    
    original = "Contact John Doe at john.doe@email.com or call (555) 123-4567."
    
    # Quick anonymization
    anon_text, mapping = quick_anonymize(original, use_llm=False)  # Use regex only for speed
    print(f"Original: {original}")
    print(f"Anonymized: {anon_text}")
    print(f"Mapping: {mapping}")
    
    # Quick deanonymization
    restored = quick_deanonymize(anon_text, mapping)
    print(f"Restored: {restored}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Web LLM workflow
    print("=== Web LLM Workflow Example ===")
    
    processor = PIIProcessor(use_llm=False)  # Use regex only for demo
    
    # Original sensitive document
    sensitive_doc = """
    Please review the contract for Sarah Johnson (SSN: 123-45-6789).
    She can be reached at sarah.j@company.com or (555) 987-6543.
    Address: 123 Main St, Anytown, NY 12345
    """
    
    # Simulate sending to web LLM (you would send anonymized_input)
    anonymized_input, _ = processor.anonymize_text(sensitive_doc, "demo_mapping.json")
    print("Text to send to web LLM:")
    print(anonymized_input)
    
    # Simulate web LLM response (containing placeholders)
    simulated_response = """
    I've reviewed the contract for [PERSON1] with SSN [SSN1].
    Their contact information is [EMAIL1] and [PHONE1].
    The address on file is [LOCATION1].
    Recommendation: Update the contract terms and send to [EMAIL1].
    """
    
    print("\nSimulated web LLM response:")
    print(simulated_response)
    
    # Restore the PII in the response
    final_response = processor.deanonymize_text(simulated_response, mapping_file="demo_mapping.json")
    print("\nFinal response with PII restored:")
    print(final_response)
    
    # Cleanup
    processor.cleanup_mapping_file() 