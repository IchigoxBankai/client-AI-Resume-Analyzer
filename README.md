# ⚡ ResuMetric AI — Next-Gen AI Resume Analyzer & Career Intelligence Suite
> **BSc Computer Science 3rd Year Final Project Submission**  
> *A high-performance AI & NLP-driven system for automated Applicant Tracking System (ATS) scoring, STAR-method bullet optimization, skill gap roadmapping, career fit prediction, and mock interview preparation.*

---

## 🌟 Key Highlights & Features

1. **Multi-Format Resume Ingestion**:
   - Parses `.pdf` (via `pdfplumber` & `pypdf`), `.docx` (via `python-docx`), and `.txt`.
   - Contact detail extraction (Email, Phone, LinkedIn, GitHub, Portfolio).
   - Smart structural section segmenter (Summary, Experience, Education, Skills, Projects, Certifications).

2. **Core ATS Scoring & Vector Matching Engine**:
   - **TF-IDF Vectorization & Cosine Similarity** matching against job descriptions.
   - 4-Pillar Weighted ATS Scoring Model (Skills Match 40%, Content Relevance 30%, STAR Action Verbs 15%, Section Layout 15%).
   - Interactive visual gauge chart and keyword pill match indicators.

3. **Curated Skill Taxonomy & Gap Roadmaps**:
   - 500+ skills categorized across 10 technology domains.
   - Identifies missing critical skills and generates curated free learning roadmaps.

4. **AI STAR-Method Resume Bullet Optimizer**:
   - Evaluates bullet points for weak verbs vs. strong power action verbs and quantified impact metrics (`%`, `$`, numbers).
   - 1-Click AI rewrite into Situation, Task, Action, Result format.

5. **Multi-Role Career Fit Predictor**:
   - Real-time compatibility index across 10+ major industry roles (Full-Stack, AI/ML, DevOps, Data Science, Frontend, Backend, etc.).

6. **AI Mock Interview Simulator**:
   - Dynamically creates customized technical & behavioral interview questions with model answers based on the candidate's actual projects and tech stack.

7. **Dual-Engine Architecture (Generative AI + Offline NLP Fallback)**:
   - Supports Google Gemini API for generative insights.
   - **Offline Mode**: Automatically falls back to high-speed local NLP rules if no API key or internet is available — zero failure risk during college presentations!

8. **Exportable PDF Audit Report**:
   - Generates and downloads a clean, publication-ready ATS Audit Report PDF using `reportlab`.

9. **Secure User Authentication & Profile Suite**:
   - Users can choose their own username, password, and display name.
   - Credentials secured with salted SHA-256 hashing and persisted in local JSON storage (`sample_data/users.json`).
   - Top-right authentication bar displaying user's name badge, active session status, and one-click logout.
   - Compulsory authentication gating for resume uploads (`.pdf`, `.docx`, `.txt`), ensuring personalized candidate intelligence reports and history tracking.

---

## 🚀 How to Run in VS Code (Step-by-Step)

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** ➔ **Open Folder...**
3. Select the `client AI resume` folder.

### Step 2: Open the Integrated Terminal in VS Code
- Press `Ctrl + ` `~` (backtick) or go to menu **Terminal** ➔ **New Terminal**.
- Ensure the terminal is in the project folder.

### Step 3: (Recommended) Create & Activate a Virtual Environment
In your VS Code terminal, run:

**For Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell shows execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then re-run the activate command).*

**For Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Project Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Launch the Application
```bash
streamlit run app.py
```
> 🎉 The application will automatically open in your default browser at `http://localhost:8501`.

---

## ⚡ 1-Click Startup (Alternative)
- **On Windows**: Double-click [`run_app.bat`](file:///c:/Users/Nishant%20Puthran/Desktop/My%20PROJECTS/client%20AI%20resume/run_app.bat) to launch instantly.
- **On Mac/Linux**: Run `./run_app.sh` in the terminal.

---

## 🌐 How to Make it LIVE (Free Public URL)

You can deploy this project for **100% FREE** on **Streamlit Community Cloud** in less than 3 minutes so anyone or your college examiners can access it via a live URL:

### Step 1: Push Code to GitHub
1. Create a free account on [GitHub.com](https://github.com).
2. Create a new repository (e.g., `ai-resume-analyzer`).
3. In your VS Code terminal, initialize and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ResuMetric AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-resume-analyzer.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `ai-resume-analyzer`, Branch: `main`, Main file path: `app.py`.
4. (Optional) In Advanced settings, add your `GEMINI_API_KEY` under Secrets.
5. Click **"Deploy!"**.
6. 🚀 Your live website link will be ready (e.g., `https://ai-resume-analyzer.streamlit.app`)!

---

## 📂 Project Architecture & Folder Structure

```
client AI resume/
├── .streamlit/
│   └── config.toml          # Custom modern dark/indigo theme configuration
├── core/
│   ├── __init__.py          # Package initializer
│   ├── parser.py            # PDF, DOCX, TXT parser & contact/section extraction
│   ├── skills_db.py         # 500+ skill taxonomy & domain learning roadmaps
│   ├── nlp_analyzer.py      # TF-IDF, Cosine Similarity, ATS scoring & bullet analysis
│   ├── ai_generator.py      # Gemini LLM integration + offline intelligent rule generator
│   ├── role_matcher.py      # Industry career profile compatibility engine
│   └── report_generator.py  # ReportLab PDF audit generator
├── sample_data/
│   ├── sample_job_descriptions.json # Standard industry JD presets
│   └── sample_resume_swe.txt        # Demo Full-Stack Engineer resume
├── app.py                   # Main Streamlit web application & UI
├── requirements.txt         # All Python package requirements
├── .env.example             # Environment template for optional API keys
├── run_app.bat              # Windows 1-click execution script
├── run_app.sh               # Mac/Linux 1-click execution script
├── PROJECT_REPORT.md        # Academic submission report & documentation
├── VIVA_PREP_GUIDE.md       # External examiner viva Q&A guide
└── README.md                # Project documentation & run guide
```

---

## 🔑 Optional: Setting Up Gemini API Key
1. Get a free Google Gemini API key at: [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Either enter it directly in the app's sidebar during runtime, OR create a `.env` file in the root folder:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. *Note: Even without an API key, the app functions 100% completely using its built-in NLP heuristics and rule engines.*
