import json
import os
import re

def load_skills_dict() -> dict:
    """Loads the skill dictionary from the JSON file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, 'data', 'skills.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_skills(text: str, skills_dict: dict) -> set:
    """Finds skills in the text based on the skills dictionary."""
    found_skills = set()
    text = text.lower()
    
    for category, skills in skills_dict.items():
        for skill in skills:
            # Word boundary regex to avoid partial matches (e.g., 'c' in 'machine')
            # Escape skill to handle special characters like '+' in 'C++'
            pattern = r'(?<![a-z0-9])' + re.escape(skill.lower()) + r'(?![a-z0-9])'
            if re.search(pattern, text):
                found_skills.add(skill.upper() if skill.lower() in {'c', 'c++', 'c#', 'sql'} else skill.title())  # Preserve common technical names
                
    return found_skills
