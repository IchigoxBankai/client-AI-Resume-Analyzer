"""
parser.py
Multi-format resume parser for PDF, DOCX, and TXT files.
Extracts raw text, contact information, metadata, and structured sections.
"""

import re
import io
from typing import Dict, Any, List, Optional

# PDF extractors
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pypdf
except ImportError:
    pypdf = None

# DOCX extractor
try:
    import docx
except ImportError:
    docx = None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using pdfplumber with pypdf fallback."""
    text = ""
    # Try pdfplumber first for superior layout handling
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            pass

    # Fallback to pypdf if pdfplumber returned empty or failed
    if not text.strip() and pypdf:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            pass

    return clean_text(text)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from DOCX file bytes."""
    if not docx:
        return ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        # Also extract text inside tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        return clean_text("\n".join(full_text))
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extracts text from TXT file bytes with encoding detection."""
    for encoding in ["utf-8", "latin-1", "windows-1252", "ascii"]:
        try:
            return clean_text(file_bytes.decode(encoding))
        except UnicodeDecodeError:
            continue
    return clean_text(file_bytes.decode("utf-8", errors="ignore"))


def clean_text(text: str) -> str:
    """Normalizes whitespace and removes unprintable characters."""
    if not text:
        return ""
    # Replace weird unicode whitespace and bullet characters
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\uf0b7\uf0a7]', '\n• ', text)
    # Normalize multiple newlines and spaces
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts email, phone, LinkedIn, GitHub, and Portfolio URLs using regex patterns.
    """
    contacts = {
        "emails": [],
        "phones": [],
        "linkedin": None,
        "github": None,
        "portfolio": None
    }
    
    # Email regex
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    contacts["emails"] = list(dict.fromkeys([e.strip('.').lower() for e in emails]))
    
    # Phone regex (Indian/US/International standard formats)
    phone_pattern = r'(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}|\b[6-9]\d{9}\b'
    raw_phones = re.findall(phone_pattern, text)
    cleaned_phones = []
    for p in raw_phones:
        cleaned = re.sub(r'[^\d+]', '', p)
        if len(cleaned) >= 10:
            cleaned_phones.append(p.strip())
    contacts["phones"] = list(dict.fromkeys(cleaned_phones))[:2]
    
    # LinkedIn
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if linkedin_match:
        contacts["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
    
    # GitHub
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if github_match:
        contacts["github"] = f"https://github.com/{github_match.group(1)}"

    # Portfolio / Web link
    portfolio_match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|me|io|tech|app|site|netlify\.app|vercel\.app|github\.io))\b', text, re.IGNORECASE)
    if portfolio_match:
        contacts["portfolio"] = portfolio_match.group(0)

    return contacts


def segment_resume_sections(text: str) -> Dict[str, str]:
    """
    Segments resume text into logical sections based on common headings.
    """
    section_patterns = {
        "summary": r"(?:summary|professional summary|profile|about me|objective|career objective)",
        "experience": r"(?:work experience|experience|employment history|work history|professional experience|internships|internship experience)",
        "education": r"(?:education|academic qualifications|academic background|academics|educational background)",
        "skills": r"(?:skills|technical skills|key skills|core competencies|technologies|tech stack|skills & expertise)",
        "projects": r"(?:projects|academic projects|key projects|personal projects|technical projects)",
        "certifications": r"(?:certifications|certificates|licenses|courses|accreditations)",
        "achievements": r"(?:achievements|honors|awards|accomplishments|extracurricular activities|publications)"
    }
    
    sections = {key: "" for key in section_patterns}
    sections["raw_header"] = ""
    
    # Find positions of headers
    lines = text.split("\n")
    current_section = "raw_header"
    collected_lines = {sec: [] for sec in sections}
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if not cleaned_line:
            continue
        
        # Check if this line is a section header
        matched_section = None
        for sec_name, pattern in section_patterns.items():
            # Check exact or short header match
            if re.fullmatch(pattern, cleaned_line) or (len(cleaned_line.split()) <= 4 and re.search(r'\b' + pattern + r'\b', cleaned_line)):
                matched_section = sec_name
                break
        
        if matched_section:
            current_section = matched_section
        else:
            collected_lines[current_section].append(line)
            
    for sec in sections:
        sections[sec] = "\n".join(collected_lines[sec]).strip()
        
    return sections


def compute_resume_statistics(text: str) -> Dict[str, Any]:
    """
    Calculates word count, reading time, sentence count, and readability stats.
    """
    words = re.findall(r'\b[A-Za-z0-9+#.-]+\b', text)
    word_count = len(words)
    char_count = len(text)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = max(1, len([s for s in sentences if s.strip()]))
    
    # Estimated reading time (average 200 words per minute)
    est_reading_minutes = round(word_count / 200.0, 1)
    
    # Approximate Flesch Reading Ease score
    syllable_count = sum(len(re.findall(r'[aeiouy]+', w.lower())) for w in words) or 1
    if word_count > 0 and sentence_count > 0:
        flesch_score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
        flesch_score = max(0.0, min(100.0, round(flesch_score, 1)))
    else:
        flesch_score = 60.0
        
    return {
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 1),
        "estimated_reading_time_min": est_reading_minutes,
        "flesch_reading_ease": flesch_score
    }
