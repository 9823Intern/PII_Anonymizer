import spacy
import re

nlp = spacy.load("en_core_web_lg")

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
            # 'DATE': 'DATE',
            # 'TIME': 'TIME',
            'MONEY': 'MONEY',
            'PHONE': 'PHONE',
            'BANK_ACCOUNT': 'BANK_ACCOUNT',
            'ROUTING_NUMBER': 'ROUTING_NUMBER',
            'SSN': 'SSN',
            'ZIP': 'ZIP',
            'CREDIT_CARD': 'CREDIT_CARD'
        }

    # def anonymize(self, data):
    #     self.data = data
    #     return self.data
    
    # def anonymize_column(self, column):
    #     return column.apply(self.anonymize_value)
    
    # def anonymize_value(self, value):
    #     return value
    def _spans_overlap(self, a_start, a_end, b_start, b_end):
        return a_start < b_end and b_start < a_end

    def _find_custom_spans(self, text):
        spans = []
        # SSN: 123-45-6789
        ssn_pattern = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
        # US phone numbers
        phone_pattern = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?|\d{3}[-.\s])\d{3}[-.\s]?\d{4}(?!\d)")
        # Credit card: 4-4-4-4 with spaces or dashes
        cc_pattern = re.compile(r"(?<!\d)(?:\d{4}[-\s]){3}\d{4}(?!\d)")
        # ZIP: capture only the zip after a US state code (to avoid generic 5-digits)
        zip_pattern = re.compile(r"\b(?:A[KLRZ]|C[AOT]|D[EC]|F[LM]|G[AU]|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|P[ARW]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])\s+(\d{5}(?:-\d{4})?)\b")
        # Bank/routing candidates
        bank_digits_pattern = re.compile(r"(?<!\d)\d{10,12}(?!\d)")
        routing_digits_pattern = re.compile(r"(?<!\d)\d{9}(?!\d)")

        for m in ssn_pattern.finditer(text):
            spans.append((m.start(), m.end(), 'SSN'))
        for m in phone_pattern.finditer(text):
            spans.append((m.start(), m.end(), 'PHONE'))
        for m in cc_pattern.finditer(text):
            spans.append((m.start(), m.end(), 'CREDIT_CARD'))
        for m in zip_pattern.finditer(text):
            spans.append((m.start(1), m.end(1), 'ZIP'))

        # Proximity-based labeling for bank account and routing numbers
        def has_keyword_before(idx, keywords, window=60):
            start = max(0, idx - window)
            ctx = text[start:idx].lower()
            return any(k in ctx for k in keywords)

        for m in routing_digits_pattern.finditer(text):
            if has_keyword_before(m.start(), ["routing", "aba", "rtg", "transit"]):
                spans.append((m.start(), m.end(), 'ROUTING_NUMBER'))

        for m in bank_digits_pattern.finditer(text):
            if has_keyword_before(m.start(), ["account", "acct", "iban", "account number"]):
                spans.append((m.start(), m.end(), 'BANK_ACCOUNT'))

        return spans

    def _find_label_spans(self, text):
        """Find uppercase label tokens like SSN, DOB, EIN, etc., and generic 2–5 letter labels
        followed by a colon or value; these should be preserved (not anonymized)."""
        spans = []
        # Specific known labels
        known_labels = ["SSN", "DOB", "EIN", "TIN", "ZIP"]
        specific_re = re.compile(r"\b(?:" + "|".join(known_labels) + r")\b")
        for m in specific_re.finditer(text):
            spans.append((m.start(), m.end()))

        # Generic uppercase labels 2–5 chars before colon or digits
        generic_re = re.compile(r"\b([A-Z]{2,5})\b(?=\s*:|\s*[-#]|\s+\d)")
        for m in generic_re.finditer(text):
            spans.append((m.start(1), m.end(1)))
        return spans

    def anonymize_data(self, file):
        self.doc = nlp(file)
        anonymized_doc = file
        
        # Reset counters for each document
        self.entity_counters = {}

        # 1) Find custom regex spans (priority over NER)
        custom_spans = self._find_custom_spans(file)
        label_spans = self._find_label_spans(file)

        # 2) Keep spaCy spans that do not overlap custom spans
        def overlaps_any(s, e, spans):
            for cs, ce, _ in spans:
                if self._spans_overlap(s, e, cs, ce):
                    return True
            return False

        def overlaps_any_protected(s, e, spans):
            for cs, ce in spans:
                if self._spans_overlap(s, e, cs, ce):
                    return True
            return False

        ent_spans = []
        for ent in self.doc.ents:
            if not overlaps_any(ent.start_char, ent.end_char, custom_spans) and not overlaps_any_protected(ent.start_char, ent.end_char, label_spans):
                ent_spans.append((ent.start_char, ent.end_char, ent.label_))

        # 3) Combine and replace from end to start to keep indices valid
        all_spans = custom_spans + ent_spans
        all_spans.sort(key=lambda x: x[0])

        for start, end, label in reversed(all_spans):
            base_label = self.label_mapping.get(label, label)
            if base_label not in self.entity_counters:
                self.entity_counters[base_label] = 0
            self.entity_counters[base_label] += 1
            placeholder = f"[{base_label}{self.entity_counters[base_label]}]"
            anonymized_doc = anonymized_doc[:start] + placeholder + anonymized_doc[end:]
            
        return anonymized_doc


if __name__ == "__main__":
    anonymizer = Anonymizer()
    text = """My name is John Doe and I live in 123 Main St, Los Angeles, USA. I work at Google, and my salary is $100,000. 
    My daughter's name is Alice Doe and she lives in 456 Oak Avenue, New York City, USA.
    If you need to contact me, you can reach me at john.doe@example.com.
    My phone number is 123-456-7890.
    My social security number is 123-45-6789.
    My credit card number is 1234-5678-9012-3456.
    My bank account routing number is 1234567890.
    My passport number is 1234567890.
    My driver's license number is 1234567890.
    My social security number is 123-45-6789.
    My credit card number is 1234-5678-9012-3456.
    """

    text2 = """
    9823 Capital LLC Employee Records - Confidential

1. Name: Johnathan Miller
   SSN: 512-48-9237
   Address: 1456 Oakridge Lane, Denver, CO 80203
   Phone: (303) 555-7284
   Email: [jmiller1984@examplemail.com](mailto:jmiller1984@examplemail.com)
   DOB: 03/14/1984

2. Name: Sarah L. Thompson
   SSN: 238-66-1092
   Address: 782 Willow Creek Rd, Austin, TX 73301
   Phone: 512-777-9912
   Email: [sarah.thompson@workmail.org](mailto:sarah.thompson@workmail.org)
   DOB: 09/21/1990

3. Name: Rajesh Patel
   SSN: 449-19-3348
   Address: 2201 Maple Avenue Apt 5B, New York, NY 10016
   Phone: 917-222-4401
   Email: [rpatel77@personalmail.net](mailto:rpatel77@personalmail.net)
   DOB: 07/07/1977

4. Name: Emily Carter
   SSN: 155-73-8245
   Address: 950 Bayshore Blvd, San Francisco, CA 94124
   Phone: 415-389-5562
   Email: [ecarter.sf@businessco.com](mailto:ecarter.sf@businessco.com)
   DOB: 12/02/1988

5. Name: Michael Rodriguez
   SSN: 601-54-2109
   Address: 321 Pine Street, Miami, FL 33130
   Phone: 305-833-4509
   Email: [mike.rodriguez305@mailservice.com](mailto:mike.rodriguez305@mailservice.com)
   DOB: 05/27/1982

---

This document contains fabricated sensitive information for testing anonymization systems only.

    """
    anonymized_doc = anonymizer.anonymize_data(text2)
    print(anonymized_doc)