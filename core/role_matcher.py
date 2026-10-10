"""
role_matcher.py
Predicts industry job role suitability based on extracted skills and resume content.
"""

from typing import Dict, Any, List
from core.skills_db import TECH_ROLES_PROFILES


def evaluate_job_roles_fit(resume_skills: List[str], resume_text: str) -> List[Dict[str, Any]]:
    """
    Evaluates how well a resume matches various software/IT job roles.
    Returns a sorted list of roles with match percentages and skill gaps.
    """
    resume_skills_lower = {s.lower() for s in resume_skills}
    resume_text_lower = resume_text.lower()
    
    results = []
    
    for role_name, required_skills in TECH_ROLES_PROFILES.items():
        req_set = set(required_skills)
        matched = []
        missing = []
        
        for skill in required_skills:
            if skill in resume_skills_lower or (f" {skill} " in f" {resume_text_lower} "):
                matched.append(skill)
            else:
                missing.append(skill)
                
        match_percentage = round((len(matched) / len(required_skills)) * 100, 1)
        
        # Categorize readiness level
        if match_percentage >= 70:
            fit_level = "High Match 🚀"
            badge_color = "success"
        elif match_percentage >= 40:
            fit_level = "Moderate Match ⚡"
            badge_color = "warning"
        else:
            fit_level = "Low Match 📚"
            badge_color = "info"
            
        results.append({
            "role": role_name,
            "match_percentage": match_percentage,
            "fit_level": fit_level,
            "badge_color": badge_color,
            "matched_skills": matched,
            "missing_skills": missing,
            "total_required": len(required_skills)
        })
        
    # Sort roles from highest match to lowest
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results
