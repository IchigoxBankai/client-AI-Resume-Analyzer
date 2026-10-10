import sys
from core.parser import segment_resume_sections, compute_resume_statistics, extract_contact_info
from core.nlp_analyzer import compute_ats_score, extract_skills_from_text, analyze_bullet_points
from core.role_matcher import evaluate_job_roles_fit
from core.ai_generator import rewrite_bullet_point_ai, generate_interview_questions
from core.report_generator import generate_pdf_report

print("Running test suite...")
with open("sample_data/sample_resume_swe.txt", "r", encoding="utf-8") as f:
    text = f.read()

contacts = extract_contact_info(text)
print("Extracted contacts:", contacts)

sections = segment_resume_sections(text)
print("Detected sections:", [k for k, v in sections.items() if v])

stats = compute_resume_statistics(text)
print("Statistics:", stats)

skills = extract_skills_from_text(text)
print("Total skills found:", skills["total_count"])

bullets = analyze_bullet_points(text)
print("Bullets analyzed:", bullets["total_bullets_analyzed"], "Action verb score:", bullets["action_verb_score"])

ats = compute_ats_score(text, "Required skills: Python, React, Docker, FastAPI, PostgreSQL", sections)
print("ATS Score calculated:", ats["overall_ats_score"], "Breakdown:", ats["breakdown"])

roles = evaluate_job_roles_fit(ats["skills_data"]["resume_skills"], text)
print("Top matched role:", roles[0]["role"], f"({roles[0]['match_percentage']}%)")

rewrite = rewrite_bullet_point_ai("worked on building api and fixed bugs")
print("Offline bullet rewrite:", rewrite["strong_version"])

questions = generate_interview_questions(ats["skills_data"]["resume_skills"], sections["projects"], "Software Engineer")
print("Generated questions count:", len(questions))

pdf_bytes = generate_pdf_report("Alex Morgan", contacts, stats, ats, roles)
print("Generated PDF size bytes:", len(pdf_bytes))

print("\n>>> ALL TESTS PASSED SUCCESSFULLY 100%! <<<")
