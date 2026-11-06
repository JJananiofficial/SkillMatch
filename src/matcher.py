import math
from collections import Counter
from src.text_processor import clean_text

def get_tf_idf_cosine_similarity(text1: str, text2: str) -> float:
    """Calculates TF-IDF and Cosine Similarity from scratch without scikit-learn."""
    words1 = text1.split()
    words2 = text2.split()
    
    if not words1 or not words2:
        return 0.0
        
    # 1. Create a vocabulary of unique words from both texts
    vocab = set(words1).union(set(words2))
    
    # 2. Term Frequency (TF)
    tf1 = Counter(words1)
    tf2 = Counter(words2)
    
    vec1 = []
    vec2 = []
    
    # 3. Calculate TF-IDF for each word in vocabulary
    for word in vocab:
        # TF = (count of word) / (total words in document)
        tf_a = tf1[word] / len(words1)
        tf_b = tf2[word] / len(words2)
        
        # IDF = log( (1 + Total Documents) / (1 + Documents containing word) ) + 1
        # Sklearn smoothed IDF formula
        doc_count = 0
        if word in tf1: doc_count += 1
        if word in tf2: doc_count += 1
        
        idf = math.log((1 + 2) / (1 + doc_count)) + 1
        
        vec1.append(tf_a * idf)
        vec2.append(tf_b * idf)
        
    # 4. Calculate Cosine Similarity: dot(A, B) / (norm(A) * norm(B))
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def calculate_match_score(resume_text: str, jd_text: str) -> int:
    """Cleans text and returns match percentage."""
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    similarity = get_tf_idf_cosine_similarity(clean_resume, clean_jd)
    percentage = round(similarity * 100)
    
    return percentage

def calculate_skill_gap(resume_skills: set, jd_skills: set) -> tuple:
    """Calculates matched and missing skills."""
    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills.difference(resume_skills)
    return matched_skills, missing_skills
