import re

def extract_main_argument(content, stance):
    """
    Extracts the core argument from a response by analyzing structural markers.
    """
    # 1. Paragraph Segmentation
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    if not paragraphs:
        return "No clear argument found."

    extracted_sentences = []
    
    # 2. Sentence Analysis
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', p)
        if sentences:
            # First sentence (typically topic sentence)
            extracted_sentences.append(sentences[0])
            # Last sentence (typically concluding sentence)
            if len(sentences) > 1:
                extracted_sentences.append(sentences[-1])

    # 3. Core Identification (Filtering for stance-bearing language)
    # This is a simplified version
    core_points = []
    for s in extracted_sentences:
        if stance.lower() == "cautious":
            if any(word in s.lower() for word in ["risk", "danger", "harm", "regulation", "safety", "limit", "caution"]):
                core_points.append(s)
        elif stance.lower() == "optimistic":
            if any(word in s.lower() for word in ["innovation", "opportunity", "benefit", "growth", "empower", "freedom", "market"]):
                core_points.append(s)
    
    if not core_points:
        return extracted_sentences[0] if extracted_sentences else "Argument extraction failed."

    # 4. Consistency Check is implicitly handled by filtering for stance words
    
    return " ".join(core_points[:2])
