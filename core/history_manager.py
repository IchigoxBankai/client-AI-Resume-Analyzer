"""
history_manager.py
Persistent storage manager for resume analysis history using local JSON file.
Ensures history records persist across server restarts and user sessions.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

HISTORY_FILE = "sample_data/analysis_history.json"


def _ensure_history_file():
    """Ensures the history storage file exists."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def get_all_history() -> List[Dict[str, Any]]:
    """Retrieves all saved analysis records sorted by date descending."""
    _ensure_history_file()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return sorted(records, key=lambda x: x.get("timestamp", ""), reverse=True)
    except Exception:
        return []


def save_analysis_record(
    resume_name: str,
    target_role: str,
    ats_score: float,
    breakdown: Dict[str, Any],
    skills_data: Dict[str, Any],
    candidate_name: str,
    raw_text: str
) -> Dict[str, Any]:
    """Saves a new analysis session record to persistent history."""
    _ensure_history_file()
    records = get_all_history()
    
    new_record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "resume_name": resume_name,
        "candidate_name": candidate_name,
        "target_role": target_role,
        "ats_score": round(float(ats_score), 1),
        "breakdown": breakdown,
        "skills_count": len(skills_data.get("resume_skills", [])),
        "matched_skills_count": len(skills_data.get("matched_skills", [])),
        "missing_skills_count": len(skills_data.get("missing_skills", [])),
        "raw_text_preview": raw_text[:500] if raw_text else "",
        "full_text": raw_text
    }
    
    # Avoid duplicate immediate saves of identical file and score
    if not any(r.get("resume_name") == resume_name and r.get("ats_score") == round(float(ats_score), 1) and r.get("target_role") == target_role for r in records[:3]):
        records.insert(0, new_record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records[:30], f, indent=2) # Keep last 30 records
            
    return new_record


def delete_history_record(record_id: str) -> bool:
    """Deletes an analysis record by its ID."""
    _ensure_history_file()
    records = get_all_history()
    filtered = [r for r in records if r.get("id") != record_id]
    if len(filtered) < len(records):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2)
        return True
    return False


def get_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single record by its ID."""
    records = get_all_history()
    for r in records:
        if r.get("id") == record_id:
            return r
    return None
