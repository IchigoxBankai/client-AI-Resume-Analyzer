"""
version_comparator.py
Evaluates and compares two resume analysis results (Version A vs Version B).
Calculates exact mathematical score deltas, newly acquired skills, resolved gaps,
and structured text differences.
"""

from typing import Dict, Any, List


def compare_resume_versions(
    res_a: Dict[str, Any],
    res_b: Dict[str, Any],
    text_a: str,
    text_b: str
) -> Dict[str, Any]:
    """
    Computes a deterministic side-by-side comparison between Version A and Version B.
    """
    score_a = res_a.get("overall_ats_score", 0.0)
    score_b = res_b.get("overall_ats_score", 0.0)
    score_delta = round(score_b - score_a, 1)
    
    # Sub-breakdown deltas
    bd_a = res_a.get("breakdown", {})
    bd_b = res_b.get("breakdown", {})
    
    sub_deltas = {
        "skills_delta": round(bd_b.get("skills_match_score", 0.0) - bd_a.get("skills_match_score", 0.0), 1),
        "relevance_delta": round(bd_b.get("content_relevance_score", 0.0) - bd_a.get("content_relevance_score", 0.0), 1),
        "action_verb_delta": round(bd_b.get("action_verb_score", 0.0) - bd_a.get("action_verb_score", 0.0), 1),
        "structure_delta": round(bd_b.get("section_structure_score", 0.0) - bd_a.get("section_structure_score", 0.0), 1)
    }
    
    # Skills changes
    skills_a = set(res_a.get("skills_data", {}).get("resume_skills", []))
    skills_b = set(res_b.get("skills_data", {}).get("resume_skills", []))
    
    matched_a = set(res_a.get("skills_data", {}).get("matched_skills", []))
    matched_b = set(res_b.get("skills_data", {}).get("matched_skills", []))
    
    new_skills = sorted(list(skills_b - skills_a))
    removed_skills = sorted(list(skills_a - skills_b))
    
    newly_matched = sorted(list(matched_b - matched_a))
    lost_matched = sorted(list(matched_a - matched_b))
    
    # Quantified bullets delta
    quant_a = res_a.get("bullet_analysis", {}).get("quantified_bullets_count", 0)
    quant_b = res_b.get("bullet_analysis", {}).get("quantified_bullets_count", 0)
    quant_delta = quant_b - quant_a
    
    # Text changes
    lines_a = set(l.strip() for l in text_a.split("\n") if len(l.strip()) > 15)
    lines_b = set(l.strip() for l in text_b.split("\n") if len(l.strip()) > 15)
    
    added_lines = [l for l in lines_b if l not in lines_a][:8]
    removed_lines = [l for l in lines_a if l not in lines_b][:8]
    
    # Deterministic factual summary bullets
    summary_insights = []
    if score_delta > 0:
        summary_insights.append(f"ATS compatibility increased by +{score_delta} points ({score_a} → {score_b}).")
    elif score_delta < 0:
        summary_insights.append(f"ATS compatibility decreased by {score_delta} points ({score_a} → {score_b}).")
    else:
        summary_insights.append(f"ATS compatibility score remained steady at {score_a}/100.")
        
    if newly_matched:
        summary_insights.append(f"Added {len(newly_matched)} target requirement matches: {', '.join(s.title() for s in newly_matched[:4])}.")
        
    if quant_delta > 0:
        summary_insights.append(f"Included {quant_delta} additional bullet points containing measurable metric outcomes.")
        
    if sub_deltas["action_verb_delta"] > 0:
        summary_insights.append(f"Action verb power index improved by +{sub_deltas['action_verb_delta']}% points.")
        
    return {
        "score_a": score_a,
        "score_b": score_b,
        "score_delta": score_delta,
        "sub_deltas": sub_deltas,
        "new_skills": new_skills,
        "removed_skills": removed_skills,
        "newly_matched": newly_matched,
        "lost_matched": lost_matched,
        "quant_a": quant_a,
        "quant_b": quant_b,
        "quant_delta": quant_delta,
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "summary_insights": summary_insights
    }
