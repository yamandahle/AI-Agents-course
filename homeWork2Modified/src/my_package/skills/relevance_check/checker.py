def check_relevance(content, topic):
    """
    Checks if the content is relevant to the topic.
    """
    topic_keywords = set(re.findall(r'\w+', topic.lower()))
    content_words = set(re.findall(r'\w+', content.lower()))
    
    # Check for overlap
    overlap = topic_keywords.intersection(content_words)
    
    # If more than 10% of topic keywords are in content, or at least 2 keywords
    if len(overlap) >= 2 or (len(topic_keywords) > 0 and len(overlap) / len(topic_keywords) > 0.1):
        return True, f"Content relevant with {len(overlap)} keyword matches."
    
    return False, "Low relevance to the topic."

import re
