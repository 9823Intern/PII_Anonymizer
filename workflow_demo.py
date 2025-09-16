#!/usr/bin/env python3
"""
Complete PII Anonymization/Deanonymization Workflow Demo

This script demonstrates:
1. Anonymizing text with PII detection
2. Saving the mapping to a file
3. Using the anonymized text (e.g., sending to web LLM)
4. Deanonymizing the response using the saved mapping
"""

from anonymize import anonymize, save_mapping_to_file
from deanonymize import deanonymize, deanonymize_from_files, save_mapping
import json

def demo_workflow():
    print("=== PII Anonymization/Deanonymization Workflow Demo ===\n")
    
    # Step 1: Original sensitive document
    original_document = """
    I'm circulating a narrative summary of the July–August accounting close and a request to confirm several upcoming wires and membership allocations. Please treat the contents below as TEST DATA; use it to validate your PII redaction workflows and indexing parsers.

Over the reporting period, Fund Alpha Partners LP (Fund Reg ID: FA-2024-0009 — TEST) recorded a preliminary net asset value (NAV) of $125,342,987 as of 2025-08-31. This figure reflects realized gains from dispersion trades and a small FX loss on the EUR/USD hedges. The back-office notes show three wires scheduled for capital calls and reimbursements:
    PRIVACY NOTE (for your pipeline tests): The paperwork also contains personally identifying information that is common in investor onboarding — tax IDs, passport numbers, residency addresses (e.g., Sophia's mailing address above), and occasional scanned driver's licenses for employees (e.g., employee Marcus D. Li, DL: D-LI-009-2023 — TEST). Ensure your anonymizer preserves formatting of masked financial tokens (e.g., masks like **** **** **** 4242), keeps date formats intact, and deterministically maps repeated identifiers to the same pseudonym across documents.
    """
    
    print("1. ORIGINAL DOCUMENT (with PII):")
    print(original_document)
    print("\n" + "="*80 + "\n")
    
    # Step 2: Anonymize the document
    anonymized_text, mapping, spans = anonymize(original_document, use_llm=True)
    
    print("2. ANONYMIZED DOCUMENT (safe for web LLM):")
    print(anonymized_text)
    print("\n" + "="*80 + "\n")
    
    print("3. MAPPING DICTIONARY:")
    print(json.dumps(mapping, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Step 3: Save mapping to file for later use
    mapping_filename = "workflow_mapping.json"
    save_mapping(mapping, mapping_filename)
    print(f"4. Mapping saved to {mapping_filename}")
    print("\n" + "="*80 + "\n")
    
    # Step 4: Simulate web LLM response (with anonymized placeholders)
    # This would normally come from an external LLM API response
    simulated_llm_response = """
    Based on the document provided, here are my observations:
    
    - [ORG1] appears to be a investment fund with registration ID [CC1]
    - The fund recorded significant NAV of $125,342,987 as of 2025-08-31
    - There are references to employees including [PERSON2] with license [CC2]
    - [PERSON1] is mentioned in the context of mailing addresses
    - The document contains standard investor onboarding information
    
    Recommendations:
    1. Ensure [ORG1] maintains proper regulatory compliance
    2. Verify that [PERSON2]'s credentials ([CC2]) are up to date
    3. Update [PERSON1]'s contact information if needed
    """
    
    print("5. SIMULATED WEB LLM RESPONSE (contains anonymized placeholders):")
    print(simulated_llm_response)
    print("\n" + "="*80 + "\n")
    
    # Step 5: Deanonymize the LLM response
    deanonymized_response = deanonymize_from_files(simulated_llm_response, mapping_filename)
    
    print("6. DEANONYMIZED LLM RESPONSE (PII restored):")
    print(deanonymized_response)
    print("\n" + "="*80 + "\n")
    
    print("✅ WORKFLOW COMPLETE!")
    print("The PII was successfully:")
    print("  • Detected and anonymized before sending to web LLM")
    print("  • Preserved in a mapping file")
    print("  • Restored in the LLM response")
    print("\nThis ensures sensitive data never leaves your environment while")
    print("still allowing you to use external LLM services safely.")

if __name__ == "__main__":
    demo_workflow() 