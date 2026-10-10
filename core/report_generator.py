"""
report_generator.py
Generates a PDF analysis report for download using ReportLab.
"""

import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(
    candidate_name: str,
    contacts: Dict[str, Any],
    stats: Dict[str, Any],
    ats_results: Dict[str, Any],
    role_fits: list
) -> bytes:
    """
    Builds an ATS Audit PDF Report.
    Returns bytes buffer for easy download in Streamlit.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor("#4f46e5") # Indigo
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    accent_green = colors.HexColor("#10b981")
    accent_amber = colors.HexColor("#f59e0b")
    bg_light = colors.HexColor("#f8fafc")
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
        leftIndent=12,
        spaceAfter=3
    )

    story = []
    
    # 1. Header Banner
    story.append(Paragraph("ResuMetric AI — Comprehensive Resume Audit Report", title_style))
    contact_str = f"Candidate Profile: <b>{candidate_name or 'Applicant'}</b> | "
    if contacts.get("emails"):
        contact_str += f"Email: {contacts['emails'][0]} | "
    if contacts.get("phones"):
        contact_str += f"Phone: {contacts['phones'][0]}"
    story.append(Paragraph(contact_str, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceBefore=0, spaceAfter=12))
    
    # 2. Executive Scorecard Table
    score = ats_results.get("overall_ats_score", 0)
    score_grade = "Excellent (A+)" if score >= 85 else "Good (B+)" if score >= 70 else "Needs Improvement (C)"
    
    scorecard_data = [
        [
            Paragraph(f"<b>Overall ATS Score:</b> <font size=14 color='#4f46e5'><b>{score} / 100</b></font> ({score_grade})", body_style),
            Paragraph(f"<b>Word Count:</b> {stats.get('word_count', 0)} words<br/><b>Readability:</b> {stats.get('flesch_reading_ease', 0)}/100", body_style)
        ]
    ]
    t_score = Table(scorecard_data, colWidths=[300, 230])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 10))
    
    # 3. Score Breakdown Sub-Scores
    breakdown = ats_results.get("breakdown", {})
    bd_data = [
        ["Evaluation Dimension", "Score", "Benchmark Status"],
        ["Skills Match & Density", f"{breakdown.get('skills_match_score', 0)}%", "Evaluated via Taxonomy & Keywords"],
        ["Semantic Relevance (TF-IDF)", f"{breakdown.get('content_relevance_score', 0)}%", "Cosine Similarity Model"],
        ["Action Verbs & Metrics", f"{breakdown.get('action_verb_score', 0)}%", "STAR Framework & Numbers"],
        ["Section Layout Completeness", f"{breakdown.get('section_structure_score', 0)}%", "Standard Headings Compliance"]
    ]
    t_bd = Table(bd_data, colWidths=[200, 110, 220])
    t_bd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
    ]))
    story.append(t_bd)
    story.append(Spacer(1, 12))
    
    # 4. Key Strengths & Areas for Improvement
    story.append(Paragraph("Key Strengths & Identified Gaps", h2_style))
    for s in ats_results.get("strengths", []):
        story.append(Paragraph(f"• <b>Strength:</b> {s}", bullet_style))
    for imp in ats_results.get("improvements", []):
        story.append(Paragraph(f"• <font color='#dc2626'><b>Gap:</b></font> {imp}", bullet_style))
    story.append(Spacer(1, 10))
    
    # 5. Skills Overview (Matched & Missing)
    skills_data = ats_results.get("skills_data", {})
    story.append(Paragraph("Skills Portfolio Analysis", h2_style))
    
    resume_skills_str = ", ".join([s.title() for s in skills_data.get("resume_skills", [])[:20]]) or "No major technical skills identified."
    story.append(Paragraph(f"<b>Extracted Skills ({len(skills_data.get('resume_skills', []))}):</b> {resume_skills_str}", body_style))
    story.append(Spacer(1, 4))
    
    if ats_results.get("has_jd_comparison"):
        matched_str = ", ".join([s.title() for s in skills_data.get("matched_skills", [])]) or "None"
        missing_str = ", ".join([s.title() for s in skills_data.get("missing_skills", [])]) or "None"
        story.append(Paragraph(f"<b>Matching Target Skills:</b> <font color='#16a34a'>{matched_str}</font>", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Missing Target Skills:</b> <font color='#dc2626'>{missing_str}</font>", body_style))
        story.append(Spacer(1, 10))
        
    # 6. Top Career Matches
    if role_fits:
        story.append(Paragraph("Industry Role Compatibility", h2_style))
        role_rows = [["Predicted Job Role", "Fit Readiness", "Matched Core Skills"]]
        for r in role_fits[:4]:
            matched_preview = ", ".join([s.title() for s in r.get("matched_skills", [])[:4]])
            role_rows.append([
                r.get("role", ""),
                f"{r.get('match_percentage', 0)}% ({r.get('fit_level', '')})",
                matched_preview or "N/A"
            ])
        t_roles = Table(role_rows, colWidths=[180, 150, 200])
        t_roles.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ]))
        story.append(t_roles)
        story.append(Spacer(1, 14))
        
    # Footer note
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=8))
    story.append(Paragraph("Generated by ResuMetric AI Academic Project Suite • Built with Python & Streamlit", subtitle_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
