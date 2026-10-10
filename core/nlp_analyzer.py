"""
nlp_analyzer.py
Core NLP & ATS evaluation engine.
Implements TF-IDF vectorization, Cosine Similarity, Skill extraction, 
Bullet point impact analysis, and multi-factor ATS scoring.
"""

import re
from typing import Dict, Any, List, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.skills_db import (
    SKILLS_TAXONOMY, ALL_SKILLS_FLAT, STRONG_ACTION_VERBS, 
    WEAK_ACTION_VERBS, SKILL_LEARNING_ROADMAPS
)


def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts and categorizes technical and soft skills from arbitrary text.
    Returns categorized dictionary and flattened set.
    """
    cleaned_lower = " " + re.sub(r'[^a-zA-Z0-9+#.-]', ' ', text.lower()) + " "
    
    categorized_skills = {}
    all_found_skills = set()
    
    for category, skill_list in SKILLS_TAXONOMY.items():
        found_in_category = []
        for skill in skill_list:
            # Match multi-word or single-word with boundary checks
            # Handle special characters like c++, c#, .net
            escaped_skill = re.escape(skill)
            pattern = rf'(?:\b|\s){escaped_skill}(?:\b|\s)'
            if re.search(pattern, cleaned_lower):
                found_in_category.append(skill)
                all_found_skills.add(skill)
                
        if found_in_category:
            categorized_skills[category] = sorted(list(set(found_in_category)))
            
    return {
        "categorized": categorized_skills,
        "all_skills": sorted(list(all_found_skills)),
        "total_count": len(all_found_skills)
    }


def analyze_bullet_points(text: str) -> Dict[str, Any]:
    """
    Analyzes resume bullet points for action verbs, measurable metrics, and weak phrases.
    """
    # Extract lines starting with bullets or numbered lists or dashes
    lines = text.split("\n")
    bullet_candidates = []
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        # Check if line is a bullet item or a standalone sentence > 3 words
        is_bullet_marker = bool(re.match(r'^(?:[•\-\*■\u2022\u2023\u25E6]|\d+\.|\([0-9a-z]\))\s*', cleaned))
        stripped_line = re.sub(r'^(?:[•\-\*■\u2022\u2023\u25E6]|\d+\.|\([0-9a-z]\))\s*', '', cleaned).strip()
        
        words = stripped_line.split()
        if (is_bullet_marker or len(words) >= 4) and len(words) <= 50:
            bullet_candidates.append(stripped_line)
            
    analyzed_bullets = []
    strong_count = 0
    weak_count = 0
    quantified_count = 0
    
    quantifiable_pattern = r'\b(?:\d+[%kKmMbB]?|\$\d+|\d+x|\d+\s*(?:percent|users|clients|requests|ms|seconds|hours|days|teams|members|projects|increase|reduction))\b'
    
    for b in bullet_candidates[:25]: # limit for clean display
        b_lower = b.lower()
        words = b_lower.split()
        first_word = words[0] if words else ""
        
        has_strong_verb = any(v in b_lower for v in STRONG_ACTION_VERBS) or (first_word in STRONG_ACTION_VERBS)
        has_weak_phrase = any(w in b_lower for w in WEAK_ACTION_VERBS)
        has_metric = bool(re.search(quantifiable_pattern, b, re.IGNORECASE))
        
        # Calculate individual bullet score (0 to 100)
        score = 50
        status = "Good"
        feedback = []
        
        if has_strong_verb:
            score += 25
            feedback.append("Uses active power verb")
        else:
            feedback.append("Missing strong action verb at start")
            
        if has_metric:
            score += 25
            quantified_count += 1
            feedback.append("Contains quantifiable results/metrics")
        else:
            feedback.append("Lacks quantifiable impact (numbers, %, or scale)")
            
        if has_weak_phrase:
            score -= 20
            weak_count += 1
            feedback.append("Contains passive/weak phrasing (e.g., 'responsible for')")
            
        score = max(20, min(100, score))
        if score >= 80:
            status = "Strong"
            strong_count += 1
        elif score <= 45:
            status = "Needs Improvement"
            weak_count += 1
            
        analyzed_bullets.append({
            "original_text": b,
            "status": status,
            "score": score,
            "has_action_verb": has_strong_verb,
            "has_metric": has_metric,
            "has_weak_phrase": has_weak_phrase,
            "feedback": feedback
        })
        
    return {
        "analyzed_bullets": analyzed_bullets,
        "total_bullets_analyzed": len(analyzed_bullets),
        "strong_bullets_count": strong_count,
        "quantified_bullets_count": quantified_count,
        "action_verb_score": round((strong_count / max(1, len(analyzed_bullets))) * 100, 1)
    }


def compute_ats_score(resume_text: str, job_description: str, resume_sections: Dict[str, str]) -> Dict[str, Any]:
    """
    Computes a comprehensive ATS score combining:
    1. TF-IDF Cosine Semantic Similarity (30%)
    2. Skills Match & Coverage Ratio (40%)
    3. Action Verbs & Quantified Results (15%)
    4. Section Completeness & Layout Standards (15%)
    """
    if not resume_text.strip():
        return {"overall_ats_score": 0, "error": "Empty resume text"}
        
    has_jd = bool(job_description and job_description.strip())
    
    # Extract skills from both
    resume_skills = extract_skills_from_text(resume_text)
    resume_skills_set = set(resume_skills["all_skills"])
    
    jd_skills_set = set()
    matched_skills = []
    missing_skills = []
    skill_match_ratio = 0.0
    cosine_sim_score = 0.0
    
    if has_jd:
        jd_skills = extract_skills_from_text(job_description)
        jd_skills_set = set(jd_skills["all_skills"])
        
        if jd_skills_set:
            matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
            missing_skills = sorted(list(jd_skills_set - resume_skills_set))
            skill_match_ratio = len(matched_skills) / max(1, len(jd_skills_set))
        else:
            # If JD had no identifiable taxonomy skills, check direct token overlap
            skill_match_ratio = 0.5
            
        # Compute TF-IDF Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            cosine_sim_score = float(sim_matrix[0][0]) * 100.0
        except Exception:
            cosine_sim_score = 50.0
    else:
        # General resume audit mode (no JD provided)
        skill_match_ratio = min(1.0, len(resume_skills_set) / 12.0)
        cosine_sim_score = 75.0 # baseline score
        
    # Bullet point analysis
    bullet_analysis = analyze_bullet_points(resume_text)
    action_verb_score = bullet_analysis["action_verb_score"]
    
    # Section completeness audit
    key_sections = ["experience", "education", "skills", "projects", "summary"]
    present_sections = [sec for sec in key_sections if resume_sections.get(sec, "").strip()]
    section_score = (len(present_sections) / len(key_sections)) * 100.0
    
    # Weighted ATS Calculation
    skill_score_val = min(100.0, skill_match_ratio * 100.0)
    
    if has_jd:
        overall_score = (
            (skill_score_val * 0.40) +
            (cosine_sim_score * 0.30) +
            (action_verb_score * 0.15) +
            (section_score * 0.15)
        )
    else:
        overall_score = (
            (skill_score_val * 0.35) +
            (action_verb_score * 0.35) +
            (section_score * 0.30)
        )
        
    overall_score = round(max(10.0, min(99.0, overall_score)), 1)
    
    # Generate tailored feedback & actionable suggestions
    feedback_strengths = []
    feedback_improvements = []
    
    if len(resume_skills_set) >= 8:
        feedback_strengths.append(f"Strong technical footprint: {len(resume_skills_set)} unique skills detected.")
    else:
        feedback_improvements.append("Skill density is low: Add more relevant tools, frameworks, and programming languages.")
        
    if bullet_analysis["quantified_bullets_count"] >= 3:
        feedback_strengths.append(f"Excellent quantifiable metrics found ({bullet_analysis['quantified_bullets_count']} impact statements with numbers/percentages).")
    else:
        feedback_improvements.append("Include more quantified achievements (e.g., 'Improved API latency by 35%', 'Scaled to 10k users').")
        
    if len(missing_skills) > 0:
        feedback_improvements.append(f"Missing {len(missing_skills)} key job requirements: {', '.join(missing_skills[:5])}...")
    elif has_jd:
        feedback_strengths.append("High skill alignment with the target job requirements!")
        
    if len(present_sections) >= 4:
        feedback_strengths.append(f"Well-structured resume layout with {len(present_sections)} core standard sections.")
    else:
        missing_sec = [s.title() for s in key_sections if s not in present_sections]
        feedback_improvements.append(f"Missing crucial standard sections: {', '.join(missing_sec)}.")
        
    # Learning roadmaps for top missing skills
    learning_recommendations = []
    for skill in missing_skills[:6]:
        if skill in SKILL_LEARNING_ROADMAPS:
            learning_recommendations.append({
                "skill": skill.title(),
                "title": SKILL_LEARNING_ROADMAPS[skill]["title"],
                "description": SKILL_LEARNING_ROADMAPS[skill]["description"],
                "link": SKILL_LEARNING_ROADMAPS[skill]["link"]
            })
            
    return {
        "overall_ats_score": overall_score,
        "has_jd_comparison": has_jd,
        "breakdown": {
            "skills_match_score": round(skill_score_val, 1),
            "content_relevance_score": round(cosine_sim_score, 1),
            "action_verb_score": round(action_verb_score, 1),
            "section_structure_score": round(section_score, 1)
        },
        "skills_data": {
            "resume_skills": resume_skills["all_skills"],
            "categorized_resume_skills": resume_skills["categorized"],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": round(skill_match_ratio * 100, 1)
        },
        "bullet_analysis": bullet_analysis,
        "present_sections": present_sections,
        "missing_sections": [s for s in key_sections if s not in present_sections],
        "strengths": feedback_strengths,
        "improvements": feedback_improvements,
        "learning_recommendations": learning_recommendations
    }
