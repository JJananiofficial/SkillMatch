import re

def clean_text(text: str) -> str:
    """
    Cleans text by removing unnecessary special characters, 
    but keeps essential ones for tech terms (e.g., C++, Node.js, C#).
    """
    if not text:
        return ""
    
    text = text.lower()
    # Keep alphanumeric, spaces, and specific symbols (+, #, ., -)
    text = re.sub(r'[^a-z0-9\s\+\#\.\-]', ' ', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()