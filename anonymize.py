import re, json, hashlib, hmac, base64
from collections import namedtuple

Span = namedtuple("Span", ["start","end","label"])

# 1) Regex detectors (expand as needed)
REGEXES = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "SSN":   re.compile(r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b"),
    # Removed PHONE, CC, IP, DATE - let LLM handle these with better context
}

def find_regex_spans(text):
    spans = []
    for label, rx in REGEXES.items():
        for m in rx.finditer(text):
            spans.append(Span(m.start(), m.end(), label))
    return spans

# 2) Optional: ask Ollama for extra spans (e.g., PERSON/ORG/LOC)
import requests

def ask_ollama_for_spans(text, model="llama3.2:3b"):
    prompt = f"""Extract PII entities from text. Return ONLY the JSON object below, nothing else:

Text to analyze:
{text}

Find these entity types:
- PERSON: Person names (first, last, full names) like "John A Doe", "Jane Smith", "Mr. Doe"
- ORG: Organization names like "Globex LLC"
- LOCATION: Addresses, cities, states like "742 Evergreen Terrace, Apt. 4B, Springfield, IL 62704"
- PHONE: Phone numbers like "(415) 555-2672" 
- DATE: Dates like "July 22, 1986", "07/22/1986"
- CC: Credit card numbers
- IP: IP addresses

Return only this JSON format:
{{"entities": [{{"text": "exact text from document", "label": "PERSON"}}]}}

Instructions:
- "text" must be the EXACT text as it appears in the document
- Focus on proper nouns and names for PERSON entities
- Do NOT include emails, SSNs, or text that contains multiple entity types
- ONLY return the JSON object, no other text"""
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    })
    r.raise_for_status()
    out = r.json()["response"]
    # print(f"DEBUG - LLM raw response: {out}")  # Uncomment for debugging
    
    # Try to extract JSON from response (in case there's extra text)
    try:
        # First try parsing the whole response
        data = json.loads(out)
    except:
        # If that fails, try to find JSON object in the response
        import re
        json_match = re.search(r'\{.*?"entities".*?\}', out, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except:
                print(f"DEBUG - Could not parse extracted JSON: {json_match.group()}")
                return []
        else:
            print(f"DEBUG - No JSON found in response")
            return []
    
    # print(f"DEBUG - LLM parsed JSON: {data}")  # Uncomment for debugging
    
    # Convert text-based entities to spans by finding their positions
    spans = []
    for entity in data.get("entities", []):
        entity_text = entity["text"]
        label = entity["label"]
        
        # Find all occurrences of this text in the document
        start = 0
        while True:
            pos = text.find(entity_text, start)
            if pos == -1:
                break
            spans.append(Span(pos, pos + len(entity_text), label))
            start = pos + 1  # Look for next occurrence
    
    return spans

# 3) Deterministic surrogate generators (format-preserving where possible)
SECRET_SALT = b"pii-anonymizer-default-salt-change-in-production"

def dhash(s: str, label: str) -> int:
    return int.from_bytes(hmac.new(SECRET_SALT, (label+"|"+s).encode(), "sha256").digest()[:8], "big")

FIRST_NAMES = ["Alex","Casey","Jordan","Taylor","Riley","Avery","Drew","Morgan","Quinn","Reese"]
LAST_NAMES  = ["Smith","Johnson","Lee","Brown","Davis","Miller","Wilson","Moore","Clark","Young"]

def surrogate_for(label, original_text, counters):
    # Simple placeholder labels with counters
    if label in counters:
        counters[label] += 1
    else:
        counters[label] = 1
    
    return f"[{label}{counters[label]}]"

def merge_and_dedupe_spans(text, spans):
    # Remove overlaps and invalid spans
    valid_spans = []
    for s in spans:
        # Skip invalid spans
        if s.start < 0 or s.end > len(text) or s.start >= s.end:
            continue
        valid_spans.append(s)
    
    # Sort by start position, then by length (prefer longer spans)
    valid_spans = sorted(valid_spans, key=lambda s: (s.start, -(s.end - s.start)))
    
    kept = []
    for s in valid_spans:
        # Check if this span overlaps with any already kept span
        overlaps = False
        for k in kept:
            if not (s.end <= k.start or s.start >= k.end):  # overlaps
                overlaps = True
                break
        if not overlaps:
            kept.append(s)
    
    # Sort final result by start position
    return sorted(kept, key=lambda s: s.start)

def anonymize(text, use_llm=False, debug=False):
    regex_spans = find_regex_spans(text)
    llm_spans = ask_ollama_for_spans(text) if use_llm else []
    
    if debug:
        print("DEBUG - Regex spans:")
        for s in regex_spans:
            print(f"  {s.label}: '{text[s.start:s.end]}' ({s.start}-{s.end})")
        print("DEBUG - LLM spans:")
        for s in llm_spans:
            print(f"  {s.label}: '{text[s.start:s.end]}' ({s.start}-{s.end})")
    
    all_spans = merge_and_dedupe_spans(text, regex_spans + llm_spans)
    
    if debug:
        print("DEBUG - Final spans after merge:")
        for s in all_spans:
            print(f"  {s.label}: '{text[s.start:s.end]}' ({s.start}-{s.end})")

    mapping = {}  # original->surrogate (store hashed key in prod)
    counters = {}  # track entity counts for numbering
    out = []
    i = 0
    for s in all_spans:
        out.append(text[i:s.start])
        original = text[s.start:s.end]
        if original not in mapping:
            mapping[original] = surrogate_for(s.label, original, counters)
        out.append(mapping[original])
        i = s.end
    out.append(text[i:])
    return "".join(out), mapping, all_spans

def save_mapping_to_file(mapping: dict, filename: str) -> None:
    """Save the mapping dictionary to a JSON file for deanonymization."""
    import json
    with open(filename, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Mapping saved to {filename}")

# Example
if __name__ == "__main__":
    doc = """
    I’m circulating a narrative summary of the July–August accounting close and a request to confirm several upcoming wires and membership allocations. Please treat the contents below as TEST DATA; use it to validate your PII redaction workflows and indexing parsers.

Over the reporting period, Fund Alpha Partners LP (Fund Reg ID: FA-2024-0009 — TEST) recorded a preliminary net asset value (NAV) of $125,342,987 as of 2025-08-31. This figure reflects realized gains from dispersion trades and a small FX loss on the EUR/USD hedges. The back-office notes show three wires scheduled for capital calls and reimbursements:
    PRIVACY NOTE (for your pipeline tests): The paperwork also contains personally identifying information that is common in investor onboarding — tax IDs, passport numbers, residency addresses (e.g., Sophia’s mailing address above), and occasional scanned driver’s licenses for employees (e.g., employee Marcus D. Li, DL: D-LI-009-2023 — TEST). Ensure your anonymizer preserves formatting of masked financial tokens (e.g., masks like **** **** **** 4242), keeps date formats intact, and deterministically maps repeated identifiers to the same pseudonym across documents.
    """
    anon, mapping, spans = anonymize(doc, use_llm=True, debug=False)
    print(anon)
    print(mapping)
