# 🎓 BSc Computer Science Viva-Voce Preparation Guide
## Project: AI Resume Analyzer — Resume Analyzer & Career Intelligence Suite

---

### Q1: What is the main objective of this project?
**Answer:** The objective of AI Resume Analyzer is to automate the analysis and scoring of resumes against target job descriptions using NLP and AI techniques. It mimics modern Applicant Tracking Systems (ATS) by calculating semantic similarity, detecting skill gaps, scoring action verbs and quantifiable metrics, and offering AI-driven STAR-method bullet optimizations.

---

### Q2: Which NLP algorithms and techniques are implemented in this project?
**Answer:** 
1. **TF-IDF (Term Frequency-Inverse Document Frequency)**: Transforms unstructured resume and job description text into numerical vector spaces.
2. **Cosine Similarity**: Calculates the angular distance between resume and job description vectors in high-dimensional space to measure semantic relevance.
3. **Regex-based Information Extraction**: Extracts emails, phone numbers, GitHub/LinkedIn links, and divides resumes into sections (Experience, Projects, Education, etc.).
4. **Keyword & Taxonomy Matching**: Compares tokens against a curated dictionary of 500+ technical skills categorized into 10 tech domains.
5. **Readability Indexing**: Computes Flesch Reading Ease scores based on sentence length and syllable count.

---

### Q3: How is the ATS score calculated?
**Answer:** The overall ATS score uses a multi-factor weighted equation:
- **40% Skill Match**: Ratio of required job skills present in the resume.
- **30% Semantic Relevance**: Cosine similarity score between the resume and JD vector representations.
- **15% Action Verbs & Quantifiable Results**: Density of strong action verbs and quantified impact metrics (percentages, numbers).
- **15% Section Completeness**: Presence of standard core sections (Summary, Experience, Skills, Education, Projects).

---

### Q4: What is the STAR method and why does your project use it?
**Answer:** STAR stands for **Situation, Task, Action, Result**. It is the gold standard framework used by recruiters and Fortune 500 hiring managers. Our system evaluates resume bullet points to ensure they start with strong action verbs and end with measurable outcomes (e.g., latency reduction, revenue increase, user count).

---

### Q5: How does your system handle resume parsing from different file types?
**Answer:** We use a multi-format parsing pipeline:
- For **PDFs**: We use `pdfplumber` for multi-column layout handling with a `pypdf` fallback.
- For **DOCX**: We use `python-docx` to extract text from paragraphs as well as embedded tables.
- For **TXT**: We use multi-encoding decoders (`utf-8`, `latin-1`, etc.) to clean and normalize text.

---

### Q6: What happens if there is no internet or no Google Gemini API key during the presentation?
**Answer:** The system is built on a **Dual-Engine Architecture**. If the Gemini API key is not present or offline, the app seamlessly falls back to our high-performance **Local Rule-Based NLP Engine**. It will still extract skills, calculate ATS scores, generate STAR bullet rewrites, provide interview questions, and export the PDF without throwing any errors.

---

### Q7: What libraries and frameworks did you use?
**Answer:**
- **Frontend & App Framework**: Streamlit (Python)
- **NLP & Machine Learning**: Scikit-Learn (TfidfVectorizer, cosine_similarity)
- **Document Parsing**: `pdfplumber`, `pypdf`, `python-docx`
- **Visualization**: Plotly Express & Plotly Graph Objects
- **Data Handling**: Pandas, NumPy
- **Generative AI**: Google Generative AI SDK (`google-generativeai`)
- **PDF Report Generation**: ReportLab

---

### Q8: What are the future enhancements for this project?
**Answer:**
1. Integrating OCR (Tesseract / EasyOCR) to parse image-scanned resumes.
2. Adding automated Resume Tailoring where an LLM rewrites the entire resume PDF automatically to match a specific job description.
3. Multi-lingual resume support for non-English languages.
