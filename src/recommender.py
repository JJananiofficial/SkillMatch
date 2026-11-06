def get_score_interpretation(score: int) -> str:
    """Returns a textual interpretation of the match score."""
    if score >= 80:
        return "Excellent Match\nYour resume is strongly aligned with this job description."
    elif score >= 60:
        return "Good Match\nYour profile matches many requirements, but some skills can be improved."
    elif score >= 40:
        return "Moderate Match\nYou have some relevant skills, but there are important gaps."
    else:
        return "Low Match\nYour current resume has significant skill gaps for this role."

def generate_recommendations(matched: set, missing: set) -> str:
    """Generates personalized next steps based on missing skills."""
    if not missing:
        return "Great job! You have all the core skills listed in the job description. Focus on tailoring your achievements to stand out."
    
    matched_list = list(matched)[:3]
    missing_list = list(missing)[:3]
    
    rec = ""
    if matched_list:
        rec += f"**Your strongest matching areas are:** {', '.join(matched_list)}.\n\n"
        
    rec += f"**The most important missing skills to focus on:** {', '.join(missing_list)}.\n\n"
    rec += "**Recommended next steps:**\n"
    
    for i, skill in enumerate(missing_list, 1):
        rec += f"{i}. Learn the fundamentals of **{skill}** and try to build a small project using it.\n"
        
    return rec
