"""
AI Resume Analyzer — Next-Gen AI Resume Analyzer & Career Intelligence Suite
Final-Year BSc Computer Science Academic Project Submission
Complete Platform Upgrade: Version Lab, AI Studio, Interview Room, & History
"""

import streamlit as st
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

# Load local environment configuration
load_dotenv()

# ==============================================================================
# CORE MODULE INTEGRATION (Preserved 100% Unchanged)
# ==============================================================================
from core.parser import (
    extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt,
    extract_contact_info, segment_resume_sections, compute_resume_statistics
)
from core.nlp_analyzer import (
    extract_skills_from_text, analyze_bullet_points, compute_ats_score
)
from core.role_matcher import evaluate_job_roles_fit
from core.ai_generator import (
    rewrite_bullet_point_ai, generate_interview_questions, 
    generate_professional_summary, improve_resume_content, evaluate_interview_answer
)
from core.report_generator import generate_pdf_report
from core.history_manager import (
    get_all_history, save_analysis_record, delete_history_record, get_record_by_id
)
from core.version_comparator import compare_resume_versions
from core.auth_manager import (
    register_user, authenticate_user, get_user_profile,
    create_user_session, verify_user_session, destroy_user_session
)


# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AI Resume Analyzer — Career Intelligence Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

if "workspace_view" not in st.session_state:
    st.session_state.workspace_view = "📑 Resume Analyzer"

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

if "active_resume_text" not in st.session_state:
    st.session_state.active_resume_text = ""

if "active_file_name" not in st.session_state:
    st.session_state.active_file_name = ""

# Authentication session state
if "session_token" not in st.session_state:
    st.session_state.session_token = ""

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "username" not in st.session_state:
    st.session_state.username = ""

# Auto-restore user authentication across browser reloads
if not st.session_state.get("is_logged_in", False):
    token_in_url = st.query_params.get("session")
    if token_in_url:
        u_profile = verify_user_session(token_in_url)
        if u_profile:
            st.session_state.is_logged_in = True
            st.session_state.user_name = u_profile.get("name", "")
            st.session_state.username = u_profile.get("username", "")
            st.session_state.session_token = token_in_url
        else:
            if "session" in st.query_params:
                del st.query_params["session"]

if "auth_notice" not in st.session_state:
    st.session_state.auth_notice = ""

# Interview session state
if "interview_session_active" not in st.session_state:
    st.session_state.interview_session_active = False

if "interview_questions_list" not in st.session_state:
    st.session_state.interview_questions_list = []

if "interview_q_index" not in st.session_state:
    st.session_state.interview_q_index = 0

if "interview_evaluations" not in st.session_state:
    st.session_state.interview_evaluations = []


# ==============================================================================
# DYNAMIC THEME TOKENS: GRADIENT RED / PINK (DARK & LIGHT MODES)
# ==============================================================================
is_dark = (st.session_state.theme_mode == "Dark")

if is_dark:
    theme_css = """
    :root {
        --bg-main: #0B0D14;
        --bg-sidebar: #0F121C;
        --surface-main: #131722;
        --surface-card: #181D2B;
        --surface-card-hover: #1E2436;
        --color-primary: #F43F5E;
        --color-primary-hover: #E11D48;
        --color-accent-pink: #FB7185;
        --color-gradient-btn: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%);
        --text-main: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --border-subtle: #242A3D;
        --border-focus: #F43F5E;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
    }
    """
    chart_bg = "#131722"
    chart_text = "#F8FAFC"
    chart_grid = "#242A3D"
else:
    theme_css = """
    :root {
        --bg-main: #F8FAFC;
        --bg-sidebar: #F1F5F9;
        --surface-main: #FFFFFF;
        --surface-card: #FFFFFF;
        --surface-card-hover: #F8FAFC;
        --color-primary: #E11D48;
        --color-primary-hover: #BE123C;
        --color-accent-pink: #E11D48;
        --color-gradient-btn: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%);
        --text-main: #0F172A;
        --text-secondary: #334155;
        --text-muted: #64748B;
        --border-subtle: #E2E8F0;
        --border-focus: #E11D48;
        --success: #059669;
        --warning: #D97706;
        --error: #DC2626;
    }
    """
    chart_bg = "#FFFFFF"
    chart_text = "#0F172A"
    chart_grid = "#E2E8F0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    {theme_css}
    
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: var(--text-main) !important;
        background-color: var(--bg-main) !important;
    }}
    
    /* Global Typography Overrides against Streamlit Emotion Cache styles */
    .stApp p,
    .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span:not(.step-badge):not(.brand-logo):not(.skill-tag),
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] b,
    [data-testid="stMarkdownContainer"] em,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6 {{
        color: var(--text-main) !important;
    }}
    
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span,
    [data-testid="stCaptionContainer"] small {{
        color: var(--text-secondary) !important;
    }}

    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {{
        color: var(--text-main) !important;
        font-weight: 600 !important;
    }}

    .main .block-container {{
        padding: 20px 32px 40px 32px !important;
        max-width: 1400px;
    }}
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}
    
    section[data-testid="stSidebar"] .block-container {{
        padding: 16px 14px 20px 14px !important;
    }}
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not(.step-badge):not(.brand-logo),
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{
        color: var(--text-main) !important;
    }}

    .brand-container {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 4px 14px 4px;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 14px;
    }}
    
    .brand-logo {{
        background: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%);
        width: 34px;
        height: 34px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.35);
    }}
    
    .brand-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-main) !important;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }}
    
    .brand-subtitle {{
        font-size: 0.62rem;
        font-weight: 700;
        color: var(--color-accent-pink) !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-top: 1px;
    }}
    
    .nav-section-label {{
        font-size: 0.66rem;
        font-weight: 700;
        color: var(--text-muted) !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 12px 2px 6px 2px;
    }}
    
    .sidebar-compact-card {{
        background: var(--surface-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
    }}
    
    .sidebar-step-header {{
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }}
    
    .step-badge {{
        background: linear-gradient(135deg, #E11D48, #F43F5E) !important;
        color: #FFFFFF !important;
        font-size: 0.62rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }}
    
    .step-heading {{
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-main) !important;
    }}
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {{
        background-color: var(--surface-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-main) !important;
        font-size: 0.82rem !important;
    }}
    
    section[data-testid="stSidebar"] .stTextArea textarea {{
        background-color: var(--surface-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-main) !important;
        font-size: 0.82rem !important;
    }}
    
    /* Radio Button Containers & Labels (Sidebar & In-Page) */
    div[data-testid="stRadio"] > div {{
        background: var(--surface-card) !important;
        padding: 4px !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-subtle) !important;
        gap: 3px !important;
    }}
    div[data-testid="stRadio"] label {{
        padding: 6px 10px !important;
        border-radius: 6px !important;
    }}
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {{
        color: var(--text-main) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stRadio"] label:hover {{
        background: var(--surface-card-hover) !important;
    }}

    .active-profile-chip {{
        background: rgba(244, 63, 94, 0.08);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 6px;
    }}
    .active-profile-chip div,
    .active-profile-chip span {{
        color: var(--text-main) !important;
    }}

    /* Selectbox Popovers & Menus */
    div[data-baseweb="select"] > div {{
        background-color: var(--surface-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-main) !important;
    }}
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {{
        color: var(--text-main) !important;
    }}
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"] ul {{
        background-color: var(--surface-main) !important;
        border: 1px solid var(--border-subtle) !important;
    }}
    li[data-baseweb="menu-item"],
    li[data-baseweb="menu-item"] div,
    li[data-baseweb="menu-item"] span {{
        color: var(--text-main) !important;
        background-color: transparent !important;
    }}
    li[data-baseweb="menu-item"]:hover {{
        background-color: var(--surface-card-hover) !important;
    }}

    /* Expanders & Accordions */
    div[data-testid="stExpander"] {{
        background-color: var(--surface-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] details {{
        background-color: var(--surface-card) !important;
    }}
    div[data-testid="stExpander"] summary {{
        background-color: var(--surface-card) !important;
        color: var(--text-main) !important;
    }}
    div[data-testid="stExpander"] summary:hover {{
        background-color: var(--surface-card-hover) !important;
    }}
    div[data-testid="stExpander"] summary svg {{
        fill: var(--text-main) !important;
        stroke: var(--text-main) !important;
        color: var(--text-main) !important;
    }}
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {{
        color: var(--text-main) !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
        background-color: var(--surface-card) !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] span {{
        color: var(--text-main) !important;
    }}

    /* Streamlit Alert Banners */
    div[data-testid="stAlert"] {{
        border-radius: 8px !important;
    }}
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {{
        color: var(--text-main) !important;
    }}

    /* Metric Cards */
    [data-testid="stMetricValue"] div {{
        color: var(--text-main) !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: var(--text-secondary) !important;
    }}

    /* Top Bar & Header */
    .top-bar-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0 12px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 14px;
    }}
    
    .breadcrumb-text {{
        font-size: 0.80rem;
        color: var(--text-secondary);
        font-weight: 500;
    }}
    .breadcrumb-active {{
        color: var(--color-accent-pink);
        font-weight: 600;
    }}
    
    .engine-status-chip {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        background: var(--surface-main) !important;
        border: 1px solid var(--border-subtle) !important;
        padding: 0 12px !important;
        border-radius: 7px !important;
        font-size: 0.76rem !important;
        color: var(--text-secondary) !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        line-height: 1 !important;
    }}
    .status-dot-green {{
        width: 6.5px;
        height: 6.5px;
        border-radius: 50%;
        background-color: var(--success);
    }}
    
    .page-header-container {{
        margin-bottom: 16px;
    }}
    .page-title {{
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--text-main);
        letter-spacing: -0.025em;
        margin: 0;
    }}
    .page-title span {{
        background: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .page-subtitle {{
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin-top: 4px;
        margin-bottom: 0;
        line-height: 1.45;
        max-width: 800px;
    }}
    
    /* Horizontal Stepper */
    .stepper-container {{
        display: flex;
        align-items: center;
        gap: 8px;
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 8px 16px;
        margin-bottom: 18px;
        height: 50px;
    }}
    
    .step-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-secondary);
    }}
    .step-item.active {{
        color: var(--color-accent-pink);
    }}
    .step-item.completed {{
        color: var(--success);
    }}
    .step-num {{
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        background: var(--surface-card);
        border: 1px solid var(--border-subtle);
    }}
    .step-num.active {{
        background: linear-gradient(135deg, #E11D48, #F43F5E);
        color: #FFFFFF;
        border-color: #F43F5E;
    }}
    .step-num.completed {{
        background: rgba(16, 185, 129, 0.15);
        color: var(--success);
        border-color: var(--success);
    }}
    .stepper-arrow {{
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 0 6px;
    }}

    /* Card Surfaces */
    .app-card {{
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }}
    
    .kpi-card {{
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 15px 16px;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card-top-accent {{
        position: absolute;
        top: 0; left: 0; right: 0; height: 2.5px;
    }}
    .kpi-title {{
        font-size: 0.70rem;
        font-weight: 700;
        color: var(--text-secondary);
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 3px;
    }}
    .kpi-desc {{
        font-size: 0.72rem;
        color: var(--text-secondary);
    }}

    /* Tags & Pills */
    .skill-tag {{
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 2px 4px 2px 0;
    }}
    .tag-matched {{
        background: rgba(16, 185, 129, 0.12);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.30);
    }}
    .tag-missing {{
        background: rgba(245, 158, 11, 0.12);
        color: var(--warning);
        border: 1px solid rgba(245, 158, 11, 0.30);
    }}
    .tag-neutral {{
        background: rgba(244, 63, 94, 0.10);
        color: var(--color-accent-pink);
        border: 1px solid rgba(244, 63, 94, 0.25);
    }}

    .hero-upload-card {{
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 22px;
        position: relative;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }}
    
    .upload-icon-circle {{
        width: 50px;
        height: 50px;
        border-radius: 12px;
        background: rgba(244, 63, 94, 0.10);
        border: 1px solid rgba(244, 63, 94, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin: 0 auto 10px auto;
        color: var(--color-accent-pink);
    }}
    
    .feature-discover-card {{
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }}
    
    .feature-row {{
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 9px 0;
        border-bottom: 1px solid var(--border-subtle);
        transition: transform 0.15s ease;
    }}
    .feature-row:last-child {{
        border-bottom: none;
        padding-bottom: 0;
    }}
    .feature-row:hover {{
        transform: translateX(3px);
    }}
    
    .feature-icon-badge {{
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: rgba(244, 63, 94, 0.10);
        border: 1px solid rgba(244, 63, 94, 0.22);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        flex-shrink: 0;
        color: var(--color-accent-pink);
        margin-top: 2px;
    }}
    
    .feature-title {{
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-main);
        margin-bottom: 2px;
    }}
    .feature-desc {{
        font-size: 0.78rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }}

    [data-testid="stFileUploader"] section {{
        background-color: var(--surface-card) !important;
        border: 1.5px dashed rgba(244, 63, 94, 0.45) !important;
        border-radius: 12px !important;
        padding: 16px 12px !important;
        transition: all 0.2s ease !important;
    }}
    [data-testid="stFileUploader"] section:hover {{
        border-color: var(--color-primary) !important;
        background-color: rgba(244, 63, 94, 0.05) !important;
        box-shadow: 0 0 18px rgba(244, 63, 94, 0.18) !important;
    }}
    [data-testid="stFileUploader"] section [data-testid="stMarkdownContainer"] p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small {{
        color: var(--text-secondary) !important;
    }}
    [data-testid="stFileUploader"] section button {{
        background-color: var(--surface-main) !important;
        border: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stFileUploader"] section button p,
    [data-testid="stFileUploader"] section button span {{
        color: var(--text-main) !important;
    }}

    .editor-diff-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 12px;
    }}
    .diff-panel {{
        background: var(--surface-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 12px 14px;
    }}
    .diff-header {{
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}
    .diff-text {{
        font-size: 0.86rem;
        color: var(--text-main);
        line-height: 1.45;
    }}

    /* Enhanced Textarea Styling for comfortable reading without scrolling */
    div[data-testid="stTextArea"] textarea {{
        font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace !important;
        font-size: 0.84rem !important;
        line-height: 1.6 !important;
        background-color: var(--surface-card) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        resize: vertical !important;
    }}
    div[data-testid="stTextArea"] textarea:focus {{
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 2px rgba(244, 63, 94, 0.2) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: var(--surface-main);
        padding: 6px;
        border-radius: 10px;
        border: 1px solid var(--border-subtle);
        margin-bottom: 16px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 16px;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.84rem;
    }}
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {{
        color: var(--text-secondary) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #E11D48, #F43F5E) !important;
        color: #FFFFFF !important;
    }}
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {{
        color: #FFFFFF !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 0.86rem;
        box-shadow: 0 4px 14px rgba(244, 63, 94, 0.3);
        transition: all 0.15s ease;
    }}
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {{
        color: #FFFFFF !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #BE123C 0%, #E11D48 50%, #F43F5E 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(244, 63, 94, 0.45);
    }}
    .stButton > button:hover p,
    .stButton > button:hover span {{
        color: #FFFFFF !important;
    }}

    /* Top Bar User Badge & Auth Styles */
    .topbar-user-badge {{
        background: rgba(244, 63, 94, 0.12) !important;
        border: 1px solid rgba(244, 63, 94, 0.35) !important;
        color: var(--text-main) !important;
        padding: 0 14px !important;
        border-radius: 7px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        line-height: 1 !important;
        box-sizing: border-box !important;
        margin: 0 !important;
    }}
    
    .user-greeting-chip {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 10px;
        background: rgba(244, 63, 94, 0.08);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 9px;
        margin-bottom: 12px;
    }}
    
    .auth-card-wrapper {{
        background: var(--surface-main);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 26px 24px 18px 24px;
        box-shadow: 0 10px 30px -6px rgba(0, 0, 0, 0.25);
        margin-bottom: 16px;
    }}
    
    .auth-avatar-banner {{
        width: 56px;
        height: 56px;
        border-radius: 14px;
        background: linear-gradient(135deg, #E11D48 0%, #F43F5E 50%, #FB7185 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        color: #FFFFFF;
        margin: 0 auto 12px auto;
        box-shadow: 0 6px 18px rgba(244, 63, 94, 0.35);
    }}

    /* Form Input Fixes: Hide overlapping helper text & keep password eye toggle clean */
    div[data-testid="InputInstructions"] {{
        display: none !important;
    }}
    div[data-baseweb="input"] button,
    div[data-baseweb="input"] button:hover,
    [data-testid="stTextInput"] button,
    [data-testid="stTextInput"] button:hover {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transform: none !important;
        min-height: 0 !important;
        height: auto !important;
        padding: 2px 6px !important;
        color: var(--text-secondary) !important;
    }}
    div[data-baseweb="input"] input {{
        padding-right: 38px !important;
    }}

    /* Topbar Layout & Straight Line Alignment */
    div[data-testid="stHorizontalBlock"]:has(#top-logout-anchor),
    div[data-testid="stHorizontalBlock"]:has(#top-login-anchor) {{
        align-items: center !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(#top-logout-anchor) > div,
    div[data-testid="stHorizontalBlock"]:has(#top-login-anchor) > div {{
        display: flex !important;
        align-items: center !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(#top-logout-anchor) div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"]:has(#top-login-anchor) div[data-testid="stVerticalBlock"] {{
        display: flex !important;
        align-items: center !important;
        gap: 0 !important;
        width: 100% !important;
    }}
    div[data-testid="element-container"]:has(#top-logout-anchor),
    div[data-testid="element-container"]:has(#top-login-anchor),
    .element-container:has(#top-logout-anchor),
    .element-container:has(#top-login-anchor) {{
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        width: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(#top-logout-anchor) .stButton,
    div[data-testid="stHorizontalBlock"]:has(#top-login-anchor) .stButton {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }}

    /* Compact Green Login Button (Top Right) */
    div[data-testid="column"]:has(#top-login-anchor) .stButton > button,
    div[data-testid="stColumn"]:has(#top-login-anchor) .stButton > button {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 7px !important;
        padding: 0 16px !important;
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        min-height: 36px !important;
        height: 36px !important;
        max-height: 36px !important;
        line-height: 36px !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.32) !important;
        transition: all 0.18s ease !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: auto !important;
        min-width: 85px !important;
        max-width: 100px !important;
        box-sizing: border-box !important;
        margin-top: 17px !important;
        margin-bottom: 0 !important;
    }}
    div[data-testid="column"]:has(#top-login-anchor) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#top-login-anchor) .stButton > button:hover {{
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.45) !important;
    }}
    div[data-testid="column"]:has(#top-login-anchor) .stButton > button p,
    div[data-testid="column"]:has(#top-login-anchor) .stButton > button span,
    div[data-testid="column"]:has(#top-login-anchor) .stButton > button div {{
        color: #FFFFFF !important;
        font-size: 0.80rem !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
    }}

    /* Compact Logout Button (Top Right) */
    div[data-testid="column"]:has(#top-logout-anchor) .stButton > button,
    div[data-testid="stColumn"]:has(#top-logout-anchor) .stButton > button {{
        background: rgba(244, 63, 94, 0.12) !important;
        color: var(--color-accent-pink) !important;
        border: 1px solid rgba(244, 63, 94, 0.35) !important;
        border-radius: 7px !important;
        padding: 0 16px !important;
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        min-height: 36px !important;
        height: 36px !important;
        max-height: 36px !important;
        line-height: 36px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        width: auto !important;
        min-width: 88px !important;
        max-width: 105px !important;
        box-sizing: border-box !important;
        margin-top: 17px !important;
        margin-bottom: 0 !important;
        overflow: visible !important;
    }}
    div[data-testid="column"]:has(#top-logout-anchor) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#top-logout-anchor) .stButton > button:hover {{
        background: rgba(244, 63, 94, 0.22) !important;
        border-color: rgba(244, 63, 94, 0.55) !important;
        transform: translateY(-1px) !important;
    }}
    div[data-testid="column"]:has(#top-logout-anchor) .stButton > button p,
    div[data-testid="column"]:has(#top-logout-anchor) .stButton > button span,
    div[data-testid="column"]:has(#top-logout-anchor) .stButton > button div {{
        color: var(--color-accent-pink) !important;
        font-size: 0.80rem !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 5px !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Compact Sidebar Theme Toggle Button */
    div[data-testid="column"]:has(#sb-theme-anchor) .stButton > button,
    section[data-testid="stSidebar"] div:has(#sb-theme-anchor) .stButton > button {{
        background: var(--surface-card) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 7px !important;
        padding: 4px 10px !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        min-height: 30px !important;
        height: 30px !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }}
    div[data-testid="column"]:has(#sb-theme-anchor) .stButton > button:hover,
    section[data-testid="stSidebar"] div:has(#sb-theme-anchor) .stButton > button:hover {{
        background: var(--surface-card-hover) !important;
        border-color: var(--color-primary) !important;
        transform: none !important;
    }}
    div[data-testid="column"]:has(#sb-theme-anchor) .stButton > button p,
    div[data-testid="column"]:has(#sb-theme-anchor) .stButton > button span {{
        color: var(--text-main) !important;
        font-size: 0.76rem !important;
    }}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SAMPLE DATA CACHES (Preserved 100% Unchanged)
# ==============================================================================
@st.cache_data
def load_sample_job_descriptions():
    try:
        with open("sample_data/sample_job_descriptions.json", "r") as f:
            return json.load(f)
    except Exception:
        return {
            "Full-Stack Software Engineer (React + Python)": "Required Skills: Python, React, JavaScript, TypeScript, FastAPI, PostgreSQL, Docker, Git, RESTful APIs, CI/CD."
        }

@st.cache_data
def load_sample_resume_text():
    try:
        with open("sample_data/sample_resume_swe.txt", "r") as f:
            return f.read()
    except Exception:
        return "Alex Morgan\nFull Stack Developer\nSkills: Python, React, TypeScript, FastAPI, PostgreSQL, Docker, Git."


sample_jds = load_sample_job_descriptions()


# ==============================================================================
# SIDEBAR NAVIGATION & CONTROLS
# ==============================================================================
with st.sidebar:
    # Brand Area
    st.markdown("""
        <div class="brand-container">
            <div class="brand-logo">⚡</div>
            <div>
                <div class="brand-title">AI Resume Analyzer</div>
                <div class="brand-subtitle">RESUME INTELLIGENCE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Left Panel Theme Toggle
    col_sb_tlabel, col_sb_tbtn = st.columns([1.2, 1.3])
    with col_sb_tlabel:
        st.markdown('<div style="font-size: 0.76rem; color: var(--text-secondary); font-weight: 600; padding-top: 5px;">🌓 Appearance</div>', unsafe_allow_html=True)
    with col_sb_tbtn:
        st.markdown('<span id="sb-theme-anchor" style="display:none;"></span>', unsafe_allow_html=True)
        theme_btn_label = "☀️ Light" if is_dark else "🌙 Dark"
        if st.button(theme_btn_label, key="sb_theme_toggle", use_container_width=True):
            st.session_state.theme_mode = "Light" if is_dark else "Dark"
            st.rerun()
            
    st.markdown('<div style="border-bottom: 1px solid var(--border-subtle); margin: 6px 0 12px 0;"></div>', unsafe_allow_html=True)
    
    # User Profile / Greeting Chip
    if st.session_state.get("is_logged_in", False):
        user_handle = st.session_state.username if ("@" in st.session_state.username) else f"@{st.session_state.username}"
        st.markdown(f"""
            <div class="user-greeting-chip">
                <span style="font-size: 1.15rem;">👤</span>
                <div style="overflow: hidden;">
                    <div style="font-size: 0.62rem; color: #FB7185; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">AUTHENTICATED USER</div>
                    <div style="font-size: 0.86rem; font-weight: 700; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.user_name}</div>
                    <div style="font-size: 0.70rem; color: var(--text-secondary);">{user_handle}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: rgba(244, 63, 94, 0.07); border: 1px dashed rgba(244, 63, 94, 0.28); border-radius: 8px; padding: 7px 10px; margin-bottom: 12px; font-size: 0.74rem; color: var(--text-secondary); text-align: center;">
                🔒 <b>Guest Mode</b> — <span style="color: var(--color-accent-pink);">Sign in to upload resumes</span>
            </div>
        """, unsafe_allow_html=True)

    # WORKSPACE NAVIGATION
    st.markdown('<div class="nav-section-label">WORKSPACE</div>', unsafe_allow_html=True)
    
    workspace_options = [
        "📑 Resume Analyzer",
        "🔬 Resume Version Lab",
        "✍️ AI Resume Studio",
        "🎙️ Mock Interview Room",
        "📜 Analysis History",
        "🔑 Login / Account"
    ]
    
    selected_view = st.radio(
        "Workspace Views",
        workspace_options,
        index=workspace_options.index(st.session_state.workspace_view) if st.session_state.workspace_view in workspace_options else 0,
        label_visibility="collapsed"
    )
    if selected_view != st.session_state.workspace_view:
        st.session_state.workspace_view = selected_view
        st.rerun()

    st.markdown('<div class="nav-section-label">ANALYSIS SETUP</div>', unsafe_allow_html=True)
    
    # Step 1: Resume Source
    st.markdown("""
        <div class="sidebar-compact-card">
            <div class="sidebar-step-header">
                <span class="step-badge">Step 1</span>
                <span class="step-heading">Resume Source</span>
            </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio(
        "Source Format",
        ["Upload Document", "Paste Resume Text", "Load Demo Profile"],
        index=0,
        label_visibility="collapsed"
    )
    
    if input_method == "Upload Document":
        if not st.session_state.get("is_logged_in", False):
            st.markdown("""
                <div style="background: rgba(244, 63, 94, 0.08); border: 1px dashed rgba(244, 63, 94, 0.35); border-radius: 8px; padding: 12px 10px; margin: 8px 0; text-align: center;">
                    <div style="font-size: 1.15rem; margin-bottom: 2px;">🔒</div>
                    <div style="font-weight: 700; font-size: 0.80rem; color: var(--text-main);">Login Required to Upload</div>
                    <div style="font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 8px; line-height: 1.35;">You must log in to upload resume documents (.pdf, .docx, .txt).</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🔑 Login to Upload", key="sidebar_login_req_btn", use_container_width=True, type="primary"):
                st.session_state.auth_notice = "Please sign in or create an account to upload your resume document."
                st.session_state.workspace_view = "🔑 Login / Account"
                st.rerun()
        else:
            uploaded_file = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx", "txt"],
                label_visibility="collapsed",
                help="Supported: PDF, DOCX, TXT. Max: 25MB."
            )
            if uploaded_file is not None:
                st.session_state.active_file_name = uploaded_file.name
                file_bytes = uploaded_file.read()
                if uploaded_file.name.endswith(".pdf"):
                    st.session_state.active_resume_text = extract_text_from_pdf(file_bytes)
                elif uploaded_file.name.endswith(".docx"):
                    st.session_state.active_resume_text = extract_text_from_docx(file_bytes)
                else:
                    st.session_state.active_resume_text = extract_text_from_txt(file_bytes)
                    
                if not st.session_state.active_resume_text.strip():
                    st.error("Could not extract text. Please ensure document is text-based.")
                else:
                    st.caption(f"✓ `{uploaded_file.name}` ({len(st.session_state.active_resume_text.split())} words)")
                
    elif input_method == "Paste Resume Text":
        pasted_text = st.text_area(
            "Paste Text",
            value=st.session_state.active_resume_text,
            height=120,
            placeholder="Paste raw resume text...",
            label_visibility="collapsed"
        )
        if pasted_text:
            st.session_state.active_resume_text = pasted_text
            st.session_state.active_file_name = "Pasted Resume"
    else: # Demo Profile
        st.session_state.active_resume_text = load_sample_resume_text()
        st.session_state.active_file_name = "Alex_Morgan_FullStack.txt"
        st.markdown('<span style="font-size: 0.76rem; color: #10B981; font-weight: 600;">✓ Demo Loaded: Alex Morgan</span>', unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 2: Target Role / JD
    st.markdown("""
        <div class="sidebar-compact-card">
            <div class="sidebar-step-header">
                <span class="step-badge">Step 2</span>
                <span class="step-heading">Target Role / JD</span>
            </div>
    """, unsafe_allow_html=True)
    
    jd_choice = st.selectbox(
        "Job Profile Selector",
        ["(Custom) Paste Custom Job Description"] + list(sample_jds.keys()),
        label_visibility="collapsed"
    )
    
    if jd_choice == "(Custom) Paste Custom Job Description":
        job_description_text = st.text_area(
            "Custom JD Content",
            height=100,
            placeholder="Paste target job requirements and duties...",
            label_visibility="collapsed"
        )
    else:
        job_description_text = sample_jds[jd_choice]
        st.markdown(f'<div style="font-size:0.72rem; color:var(--text-secondary); background:var(--surface-card); padding:5px 7px; border-radius:6px; margin-top:5px; line-height:1.3; border: 1px solid var(--border-subtle);"><b>Benchmark:</b> {jd_choice}</div>', unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Active Profile Chip
    if st.session_state.active_resume_text.strip():
        preview_lines = [l.strip() for l in st.session_state.active_resume_text.split("\n") if l.strip()]
        p_name = preview_lines[0] if preview_lines else "Candidate Resume"
        if len(p_name) > 26:
            p_name = p_name[:26]
            
        st.markdown(f"""
            <div class="active-profile-chip">
                <div style="font-size:0.65rem; color:#FB7185; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">ACTIVE RESUME</div>
                <div style="font-size:0.86rem; font-weight:700; color:var(--text-main); margin-top:2px;">{p_name}</div>
                <div style="font-size:0.70rem; color:var(--text-secondary); margin-top:1px;">{len(st.session_state.active_resume_text.split())} words ready for evaluation</div>
            </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TOP BAR WITH AUTHENTICATION
# ==============================================================================
col_tb_left, col_tb_right = st.columns([1.5, 2.5])

with col_tb_left:
    st.markdown(f"""
    <div style="padding: 8px 0;">
        <span class="breadcrumb-text">Workspace / <span class="breadcrumb-active">{st.session_state.workspace_view}</span></span>
    </div>
    """, unsafe_allow_html=True)

with col_tb_right:
    if not st.session_state.get("is_logged_in", False):
        col_t_info, col_t_login = st.columns([2.8, 0.7])
        with col_t_info:
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; height: 36px;">
                <div class="engine-status-chip">
                    <span class="status-dot-green"></span>
                    <span>Dual-Engine Online</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_t_login:
            st.markdown('<span id="top-login-anchor" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("🔑 Login", key="top_login_btn"):
                st.session_state.auth_notice = ""
                st.session_state.workspace_view = "🔑 Login / Account"
                st.rerun()
    else:
        col_t_info, col_t_logout = st.columns([3.3, 0.7])
        with col_t_info:
            display_name = st.session_state.user_name or st.session_state.username
            if len(display_name) > 16:
                display_name = display_name[:14] + "…"
            user_handle = st.session_state.username if ("@" in st.session_state.username) else f"@{st.session_state.username}"
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; height: 36px;">
                <div class="engine-status-chip">
                    <span class="status-dot-green"></span>
                    <span>Dual-Engine Online</span>
                </div>
                <div class="topbar-user-badge" title="Signed in as {st.session_state.user_name} ({user_handle})">
                    <span>👤</span>
                    <span style="font-weight: 600; font-size: 0.82rem; white-space: nowrap;">{display_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_t_logout:
            st.markdown('<span id="top-logout-anchor" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("🚪 Logout", key="top_logout_btn"):
                if st.session_state.get("session_token"):
                    destroy_user_session(st.session_state.session_token)
                st.session_state.is_logged_in = False
                st.session_state.user_name = ""
                st.session_state.username = ""
                st.session_state.session_token = ""
                if "session" in st.query_params:
                    del st.query_params["session"]
                st.rerun()

st.markdown('<div style="border-bottom: 1px solid var(--border-subtle); margin-bottom: 14px;"></div>', unsafe_allow_html=True)


# ==============================================================================
# WORKSPACE ROUTER
# ==============================================================================

# ------------------------------------------------------------------------------
# ROUTE 1: RESUME ANALYZER (PRIMARY WORKSPACE)
# ------------------------------------------------------------------------------
if st.session_state.workspace_view == "📑 Resume Analyzer":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">Resume <span>Analyzer</span></h1>
        <p class="page-subtitle">
            Understand your resume's strengths, discover skill gaps, and evaluate your compatibility with your target role.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Workflow Stepper
    step1_done = bool(st.session_state.active_resume_text.strip())
    step2_done = bool(job_description_text.strip())
    step3_done = step1_done

    st.markdown(f"""
    <div class="stepper-container">
        <div class="step-item {'completed' if step1_done else 'active'}">
            <div class="step-num {'completed' if step1_done else 'active'}">{'✓' if step1_done else '1'}</div>
            <span>Resume Source</span>
        </div>
        <div class="stepper-arrow">→</div>
        <div class="step-item {'completed' if step2_done else 'active' if step1_done else ''}">
            <div class="step-num {'completed' if step2_done else 'active' if step1_done else ''}">{'✓' if step2_done else '2'}</div>
            <span>Target Role</span>
        </div>
        <div class="stepper-arrow">→</div>
        <div class="step-item {'active' if step3_done else ''}">
            <div class="step-num {'active' if step3_done else ''}">3</div>
            <span>Analysis Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Empty State with In-Box Upload
    if not st.session_state.active_resume_text or not st.session_state.active_resume_text.strip():
        col_hero, col_info = st.columns([1.35, 1], gap="large")
        
        with col_hero:
            if not st.session_state.get("is_logged_in", False):
                st.markdown("""<div class="hero-upload-card" style="text-align: center; border: 1px solid rgba(244, 63, 94, 0.35);">
    <div class="upload-icon-circle" style="background: rgba(244, 63, 94, 0.15);">🔒</div>
    <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 6px 0; color: var(--text-main);">Login Required to Upload Resume</h3>
    <p style="color: var(--text-secondary); font-size: 0.85rem; max-width: 460px; margin: 0 auto 16px auto; line-height: 1.45;">
    To upload your resume document and receive personalized career analysis, please sign in or create an account with your name first.
    </p>
    </div>""", unsafe_allow_html=True)
                if st.button("🔑 Sign In / Create Account to Upload", type="primary", use_container_width=True, key="hero_login_btn"):
                    st.session_state.auth_notice = "Please sign in or create an account to upload your resume document."
                    st.session_state.workspace_view = "🔑 Login / Account"
                    st.rerun()
                    
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("⚡ Preview with Demo Profile", use_container_width=True):
                        st.session_state.active_resume_text = load_sample_resume_text()
                        st.session_state.active_file_name = "Alex_Morgan_FullStack.txt"
                        st.rerun()
                with col_btn2:
                    with st.popover("📝 Paste Resume Text", use_container_width=True):
                        p_text_center = st.text_area("Paste Resume Text Here:", height=140)
                        if st.button("Analyze Pasted Text", type="primary", use_container_width=True):
                            if p_text_center.strip():
                                st.session_state.active_resume_text = p_text_center
                                st.session_state.active_file_name = "Pasted Resume"
                                st.rerun()
            else:
                user_greet = f", {st.session_state.user_name}" if st.session_state.user_name else ""
                st.markdown(f"""<div class="hero-upload-card" style="text-align: center;">
    <div class="upload-icon-circle">📄</div>
    <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 6px 0; color: var(--text-main);">Ready to analyze your resume{user_greet}?</h3>
    <p style="color: var(--text-secondary); font-size: 0.85rem; max-width: 460px; margin: 0 auto 16px auto; line-height: 1.45;">
    Upload your resume to discover strengths, skill gaps, and job compatibility. Supported formats: PDF, DOCX, TXT.
    </p>
    </div>""", unsafe_allow_html=True)
                
                center_file = st.file_uploader(
                    "Upload Resume Document",
                    type=["pdf", "docx", "txt"],
                    key="center_uploader",
                    label_visibility="collapsed",
                    help="Supported: PDF, Microsoft Word (.docx), or plain text (.txt)."
                )
                if center_file is not None:
                    st.session_state.active_file_name = center_file.name
                    c_bytes = center_file.read()
                    if center_file.name.endswith(".pdf"):
                        st.session_state.active_resume_text = extract_text_from_pdf(c_bytes)
                    elif center_file.name.endswith(".docx"):
                        st.session_state.active_resume_text = extract_text_from_docx(c_bytes)
                    else:
                        st.session_state.active_resume_text = extract_text_from_txt(c_bytes)
                    st.rerun()
                    
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("⚡ Load Demo Candidate Profile", use_container_width=True):
                        st.session_state.active_resume_text = load_sample_resume_text()
                        st.session_state.active_file_name = "Alex_Morgan_FullStack.txt"
                        st.rerun()
                with col_btn2:
                    with st.popover("📝 Paste Resume Text", use_container_width=True):
                        p_text_center = st.text_area("Paste Resume Text Here:", height=140)
                        if st.button("Analyze Pasted Text", type="primary", use_container_width=True):
                            if p_text_center.strip():
                                st.session_state.active_resume_text = p_text_center
                                st.session_state.active_file_name = "Pasted Resume"
                                st.rerun()
            
        with col_info:
            st.markdown("""<div class="feature-discover-card">
    <h4 style="font-size: 0.95rem; font-weight: 700; margin: 0 0 14px 0; color: var(--text-main);">What you'll discover</h4>
    <div class="feature-row">
    <div class="feature-icon-badge">🎯</div>
    <div>
    <div class="feature-title">ATS Compatibility</div>
    <div class="feature-desc">Multi-pillar weighted resume scoring and semantic keyword alignment.</div>
    </div>
    </div>
    <div class="feature-row">
    <div class="feature-icon-badge">🧠</div>
    <div>
    <div class="feature-title">Skill Gap Analysis</div>
    <div class="feature-desc">Detects missing job requirements with curated free learning roadmaps.</div>
    </div>
    </div>
    <div class="feature-row">
    <div class="feature-icon-badge">✍️</div>
    <div>
    <div class="feature-title">STAR Bullet Optimization</div>
    <div class="feature-desc">Transforms passive lines into high-impact, quantified action bullets.</div>
    </div>
    </div>
    <div class="feature-row">
    <div class="feature-icon-badge">🎙️</div>
    <div>
    <div class="feature-title">AI Interview Preparation</div>
    <div class="feature-desc">Generates technical deep-dive questions based on your actual projects.</div>
    </div>
    </div>
    </div>""", unsafe_allow_html=True)
        st.stop()

    # Core Execution Pipeline
    with st.spinner("Evaluating resume semantics, extracting skill taxonomy, and calculating ATS score..."):
        contact_data = extract_contact_info(st.session_state.active_resume_text)
        sections_data = segment_resume_sections(st.session_state.active_resume_text)
        stats_data = compute_resume_statistics(st.session_state.active_resume_text)
        ats_results = compute_ats_score(st.session_state.active_resume_text, job_description_text, sections_data)
        role_fits = evaluate_job_roles_fit(ats_results["skills_data"]["resume_skills"], st.session_state.active_resume_text)
        
        lines = [l.strip() for l in st.session_state.active_resume_text.split("\n") if l.strip()]
        extracted_name = lines[0] if lines else "Candidate Profile"
        if len(extracted_name) > 35:
            extracted_name = extracted_name[:35]
        # Display authenticated user's name across the application if logged in
        candidate_name = st.session_state.user_name if (st.session_state.get("is_logged_in") and st.session_state.user_name) else extracted_name
            
        # Automatically save to persistent history if not already saved
        save_analysis_record(
            resume_name=st.session_state.active_file_name or "Resume Document",
            target_role=jd_choice,
            ats_score=ats_results["overall_ats_score"],
            breakdown=ats_results["breakdown"],
            skills_data=ats_results["skills_data"],
            candidate_name=candidate_name,
            raw_text=st.session_state.active_resume_text
        )

    # KPI Summary Grid
    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
    with col_k1:
        ats_score = ats_results["overall_ats_score"]
        score_accent = "#10B981" if ats_score >= 75 else "#F59E0B" if ats_score >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-top-accent" style="background: {score_accent};"></div>
            <div class="kpi-title">Overall ATS Score</div>
            <div class="kpi-value" style="color: {score_accent};">{ats_score}<span style="font-size: 0.90rem; color: var(--text-muted);">/100</span></div>
            <div class="kpi-desc">{'Top Tier Candidate' if ats_score >= 75 else 'Moderate Alignment' if ats_score >= 50 else 'Optimization Needed'}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k2:
        num_skills = len(ats_results["skills_data"]["resume_skills"])
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-top-accent" style="background: #F43F5E;"></div>
            <div class="kpi-title">Skills Identified</div>
            <div class="kpi-value" style="color: #FB7185;">{num_skills}</div>
            <div class="kpi-desc">Across 10 Tech Domains</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k3:
        act_verb_score = ats_results["breakdown"]["action_verb_score"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-top-accent" style="background: #38BDF8;"></div>
            <div class="kpi-title">Action Verb Power</div>
            <div class="kpi-value" style="color: #38BDF8;">{act_verb_score}%</div>
            <div class="kpi-desc">{ats_results['bullet_analysis']['quantified_bullets_count']} Quantified Metrics</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k4:
        readability = stats_data["flesch_reading_ease"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-top-accent" style="background: #A78BFA;"></div>
            <div class="kpi-title">Readability Index</div>
            <div class="kpi-value" style="color: #A78BFA;">{readability}</div>
            <div class="kpi-desc">Flesch Reading Ease</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k5:
        top_role = role_fits[0]["role"] if role_fits else "Software Engineer"
        top_role_pct = role_fits[0]["match_percentage"] if role_fits else 85
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-top-accent" style="background: #E11D48;"></div>
            <div class="kpi-title">Top Role Match</div>
            <div class="kpi-value" style="color: #F43F5E; font-size: 1.10rem; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{top_role}">{top_role}</div>
            <div class="kpi-desc" style="color: #10B981;">{top_role_pct}% Compatibility</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Tabs Dashboard
    tabs = st.tabs([
        "📊 ATS Scorecard & Breakdown",
        "🎯 Identified Skills by Domain",
        "✍️ STAR Bullet Health",
        "💼 Career Role Compatibility",
        "📄 Audit Summary & PDF Export"
    ])

    with tabs[0]:
        col_t1_left, col_t1_right = st.columns([1.1, 1], gap="medium")
        with col_t1_left:
            st.markdown("### 🏆 ATS Score & Factor Breakdown")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ats_results["overall_ats_score"],
                number={'suffix': "/100", 'font': {'size': 40, 'color': chart_text, 'family': 'Inter'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': chart_grid, 'tickfont': {'color': chart_text}},
                    'bar': {'color': "#F43F5E", 'thickness': 0.28},
                    'bgcolor': chart_bg,
                    'borderwidth': 1,
                    'bordercolor': chart_grid,
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                        {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.15)'},
                        {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.15)'}
                    ],
                    'threshold': {'line': {'color': "#10B981", 'width': 3}, 'thickness': 0.75, 'value': 80}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, font={'color': chart_text, 'family': "Inter"}, height=240, margin=dict(l=20, r=20, t=15, b=15))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            bd = ats_results["breakdown"]
            st.markdown(f"**🎯 Skills Match & Density (`{bd['skills_match_score']}%`):**")
            st.progress(bd['skills_match_score'] / 100.0)
            st.markdown(f"**🧠 Semantic Relevance (TF-IDF Cosine `{bd['content_relevance_score']}%`):**")
            st.progress(bd['content_relevance_score'] / 100.0)
            st.markdown(f"**⚡ Action Verbs & Metrics (`{bd['action_verb_score']}%`):**")
            st.progress(bd['action_verb_score'] / 100.0)
            st.markdown(f"**📋 Section Structure Completeness (`{bd['section_structure_score']}%`):**")
            st.progress(bd['section_structure_score'] / 100.0)

        with col_t1_right:
            st.markdown("### 🔍 Target Keyword Alignment Matrix")
            skills_data = ats_results["skills_data"]
            if ats_results["has_jd_comparison"]:
                st.markdown(f"**✅ Matching Target Keywords ({len(skills_data['matched_skills'])}):**")
                if skills_data["matched_skills"]:
                    pills_html = "".join([f'<span class="skill-tag tag-matched">{s.upper()}</span>' for s in skills_data["matched_skills"]])
                    st.markdown(f'<div style="margin-bottom: 14px;">{pills_html}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No direct keyword matches found.")
                st.markdown(f"**⚠️ Missing Target Keywords ({len(skills_data['missing_skills'])}):**")
                if skills_data["missing_skills"]:
                    missing_pills = "".join([f'<span class="skill-tag tag-missing">{s.upper()}</span>' for s in skills_data["missing_skills"]])
                    st.markdown(f'<div style="margin-bottom: 14px;">{missing_pills}</div>', unsafe_allow_html=True)
                else:
                    st.success("🎉 All target keywords are present in your resume!")
            st.markdown("---")
            st.markdown("### 💡 Key Strategic Audit Insights")
            for s in ats_results.get("strengths", []):
                st.markdown(f"✅ **Strength:** {s}")
            for imp in ats_results.get("improvements", []):
                st.markdown(f"⚠️ **Action Item:** {imp}")

    with tabs[1]:
        col_sk_l, col_sk_c, col_sk_r = st.columns([1, 3.2, 1])
        with col_sk_c:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="margin-bottom: 6px; font-weight: 800; color: var(--text-main);">📑 Identified Skills by Domain</h3>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                    Categorized overview of technical capabilities detected across your resume.
                </p>
            </div>
            """, unsafe_allow_html=True)
            categorized = ats_results["skills_data"]["categorized_resume_skills"]
            if categorized:
                for cat_name, skill_list in categorized.items():
                    with st.expander(f"🔹 {cat_name} ({len(skill_list)})", expanded=True):
                        badges_html = "".join([f'<span class="skill-tag tag-neutral">{s.title()}</span>' for s in skill_list])
                        st.markdown(f'<div style="line-height: 2.2;">{badges_html}</div>', unsafe_allow_html=True)
            else:
                st.info("No categorized skills detected in the resume text.")

    with tabs[2]:
        st.markdown("### 📋 Detected Bullet Points & Action Verb Health")
        bullets = ats_results["bullet_analysis"]["analyzed_bullets"]
        if bullets:
            for i, b in enumerate(bullets[:10]):
                status_color = "#10B981" if b["status"] == "Strong" else "#F59E0B"
                st.markdown(f"""
                <div class="app-card" style="margin-bottom: 8px; padding: 12px 14px; border-left: 3px solid {status_color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 0.74rem; font-weight: 700; color: {status_color};">{b['status'].upper()} (Score: {b['score']}/100)</span>
                    </div>
                    <div style="font-size: 0.86rem; color: var(--text-main); margin-top: 4px;">{b['original_text']}</div>
                    <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;">Feedback: {", ".join(b['feedback'])}</div>
                </div>
                """, unsafe_allow_html=True)
            st.info("💡 To optimize bullet points into high-impact STAR statements, switch to the **'✍️ AI Resume Studio'** in the left sidebar!")
        else:
            st.warning("No explicit bullet points detected.")

    with tabs[3]:
        col_r1, col_r2 = st.columns([1.1, 1], gap="medium")
        with col_r1:
            df_roles = pd.DataFrame(role_fits)
            fig_roles = px.bar(
                df_roles.sort_values(by="match_percentage", ascending=True),
                x="match_percentage", y="role", orientation="h", text="match_percentage",
                color="match_percentage", color_continuous_scale=["#EF4444", "#F59E0B", "#F43F5E", "#10B981"],
                title="Industry Role Match Probability (%)"
            )
            fig_roles.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
            fig_roles.update_layout(
                paper_bgcolor=chart_bg,
                plot_bgcolor=chart_bg,
                font={'color': chart_text, 'family': "Inter"},
                xaxis=dict(tickfont=dict(color=chart_text), title=dict(text="Compatibility (%)", font=dict(color=chart_text))),
                yaxis=dict(tickfont=dict(color=chart_text)),
                coloraxis_colorbar=dict(tickfont=dict(color=chart_text)),
                yaxis_title="",
                height=380,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        with col_r2:
            st.subheader("🎯 Role Compatibility Breakdown")
            for r in role_fits[:4]:
                matched_str = ", ".join([s.title() for s in r["matched_skills"][:4]]) or "None"
                missing_str = ", ".join([s.title() for s in r["missing_skills"][:4]]) or "None"
                st.markdown(f"""
                <div class="app-card" style="margin-bottom: 8px; padding: 12px 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: var(--text-main); font-size: 0.92rem;">{r['role']}</span>
                        <span style="font-weight: 700; color: #FB7185; font-size: 0.98rem;">{r['match_percentage']}%</span>
                    </div>
                    <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 3px;">Status: {r['fit_level']}</div>
                    <div style="font-size: 0.76rem; color: #10B981; margin-top: 3px;"><b>Skills You Have:</b> {matched_str}</div>
                    <div style="font-size: 0.76rem; color: #F59E0B; margin-top: 2px;"><b>Skills to Learn:</b> {missing_str}</div>
                </div>
                """, unsafe_allow_html=True)

    with tabs[4]:
        col_p1, col_p2 = st.columns([1, 1], gap="medium")
        with col_p1:
            st.subheader("📑 Candidate Contact & Section Health")
            st.markdown(f"**Candidate Name:** `{candidate_name}`")
            if contact_data["emails"]: st.markdown(f"**Email:** `{contact_data['emails'][0]}`")
            if contact_data["phones"]: st.markdown(f"**Phone:** `{contact_data['phones'][0]}`")
            st.markdown("---")
            for sec in ["experience", "education", "skills", "projects", "summary"]:
                has_sec = bool(sections_data.get(sec, "").strip())
                st.markdown(f"- **{sec.title()} Section:** {'✅ Detected' if has_sec else '⚠️ Missing'}")
        with col_p2:
            st.subheader("📥 Export Official ATS Audit Report (PDF)")
            pdf_bytes = generate_pdf_report(candidate_name=candidate_name, contacts=contact_data, stats=stats_data, ats_results=ats_results, role_fits=role_fits)
            st.download_button(label="⬇️ Download ATS Audit Report (PDF)", data=pdf_bytes, file_name=f"AI_Resume_Analyzer_Audit_Report_{candidate_name.replace(' ', '_')}.pdf", mime="application/pdf", type="primary", use_container_width=True)



# ------------------------------------------------------------------------------
# ROUTE 2: RESUME VERSION LAB (FEATURE ONE)
# ------------------------------------------------------------------------------
elif st.session_state.workspace_view == "🔬 Resume Version Lab":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">Resume <span>Version Lab</span></h1>
        <p class="page-subtitle">
            Compare two resume iterations side-by-side using real ATS scoring models to measure exact quantifiable improvements.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_upload_b, col_sync = st.columns([3, 1])
    with col_upload_b:
        with st.expander("📂 Optional: Upload Version B Document (.pdf, .docx, .txt)", expanded=False):
            if not st.session_state.get("is_logged_in", False):
                st.info("🔒 Login required to upload files. You can type, paste, or modify Version B directly in the editor below.")
            else:
                v_b_upload = st.file_uploader("Upload updated resume to compare against Version A:", type=["pdf", "docx", "txt"], key="lab_upload_b")
                if v_b_upload is not None:
                    vb_bytes = v_b_upload.read()
                    if v_b_upload.name.endswith(".pdf"): text_v_b_loaded = extract_text_from_pdf(vb_bytes)
                    elif v_b_upload.name.endswith(".docx"): text_v_b_loaded = extract_text_from_docx(vb_bytes)
                    else: text_v_b_loaded = extract_text_from_txt(vb_bytes)
                    if text_v_b_loaded:
                        st.session_state.lab_text_b = text_v_b_loaded
                        st.success(f"✓ Loaded '{v_b_upload.name}' into Version B editor!")
    with col_sync:
        if st.button("📋 Reset from Version A", use_container_width=True):
            st.session_state.lab_text_b = st.session_state.active_resume_text
            st.rerun()

    col_v1, col_v2 = st.columns([1, 1], gap="large")
    
    with col_v1:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 700; color: #FB7185; font-size: 0.95rem;">📌 Version A (Original Baseline)</div>
            <span style="font-size: 0.72rem; color: var(--text-secondary); background: var(--surface-card); padding: 3px 8px; border-radius: 6px; border: 1px solid var(--border-subtle);">Active Resume</span>
        </div>
        """, unsafe_allow_html=True)
        text_v_a = st.text_area(
            "Version A Content",
            value=st.session_state.active_resume_text,
            height=460,
            key="lab_text_a",
            label_visibility="collapsed"
        )
        
    with col_v2:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 700; color: #29D9A0; font-size: 0.95rem;">🚀 Version B (Target Iteration)</div>
            <span style="font-size: 0.72rem; color: #29D9A0; background: rgba(41, 217, 160, 0.1); padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(41, 217, 160, 0.25);">Editable Draft</span>
        </div>
        """, unsafe_allow_html=True)
        initial_b = st.session_state.get("lab_text_b", st.session_state.active_resume_text)
        text_v_b = st.text_area(
            "Version B Content",
            value=initial_b,
            height=460,
            key="lab_text_b",
            label_visibility="collapsed"
        )

    if st.button("🔬 Execute Side-by-Side Version Comparison", type="primary", use_container_width=True):
        if not text_v_a.strip() or not text_v_b.strip():
            st.error("Please provide text for both Version A and Version B to evaluate.")
        elif text_v_a.strip() == text_v_b.strip():
            st.warning("Version A and Version B are identical. Modify Version B to observe score deltas.")
        else:
            with st.spinner("Calculating dual ATS vector similarities and delta differentials..."):
                sec_a = segment_resume_sections(text_v_a)
                sec_b = segment_resume_sections(text_v_b)
                ats_a = compute_ats_score(text_v_a, job_description_text, sec_a)
                ats_b = compute_ats_score(text_v_b, job_description_text, sec_b)
                comp = compare_resume_versions(ats_a, ats_b, text_v_a, text_v_b)
                
                # Comparison Scoreboard
                st.markdown("### 📊 Version Evaluation Scorecard")
                col_sc1, col_sc2, col_sc3 = st.columns(3)
                
                with col_sc1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Version A (Original)</div>
                        <div class="kpi-value" style="color: #94A3B8;">{comp['score_a']}<span style="font-size:0.9rem;">/100</span></div>
                        <div class="kpi-desc">Baseline ATS Compatibility</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_sc2:
                    delta_color = "#10B981" if comp['score_delta'] > 0 else "#EF4444" if comp['score_delta'] < 0 else "#94A3B8"
                    delta_sign = f"+{comp['score_delta']}" if comp['score_delta'] > 0 else str(comp['score_delta'])
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-card-top-accent" style="background: {delta_color};"></div>
                        <div class="kpi-title">Score Differential</div>
                        <div class="kpi-value" style="color: {delta_color};">{delta_sign} pts</div>
                        <div class="kpi-desc">{'Improvement Detected 🚀' if comp['score_delta'] > 0 else 'Score Decreased ⚠️' if comp['score_delta'] < 0 else 'No Change'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_sc3:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Version B (Updated)</div>
                        <div class="kpi-value" style="color: #FB7185;">{comp['score_b']}<span style="font-size:0.9rem;">/100</span></div>
                        <div class="kpi-desc">Updated ATS Compatibility</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.markdown("#### 🎯 Factual Metric Deltas")
                    for s in comp["summary_insights"]:
                        st.markdown(f"• **{s}**")
                    if comp["newly_matched"]:
                        st.markdown("**Newly Matched Job Keywords:**")
                        pills = "".join([f'<span class="skill-tag tag-matched">{s.upper()}</span>' for s in comp["newly_matched"]])
                        st.markdown(pills, unsafe_allow_html=True)
                with col_det2:
                    st.markdown("#### 📝 Detected Content Additions")
                    if comp["added_lines"]:
                        for l in comp["added_lines"][:4]:
                            st.markdown(f"➕ `<font color='#10B981'>{l[:90]}...</font>`", unsafe_allow_html=True)
                    else:
                        st.caption("No significant single line additions detected.")
                        
                if st.button("✅ Adopt Version B as Active Resume in Workspace", use_container_width=True):
                    st.session_state.active_resume_text = text_v_b
                    st.session_state.active_file_name = "Improved_Resume_V2.txt"
                    st.success("Version B adopted! Navigating to Resume Analyzer...")
                    st.session_state.workspace_view = "📑 Resume Analyzer"
                    st.rerun()


# ------------------------------------------------------------------------------
# ROUTE 3: AI RESUME STUDIO (FEATURE THREE)
# ------------------------------------------------------------------------------
elif st.session_state.workspace_view == "✍️ AI Resume Studio":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">AI Resume <span>Studio</span></h1>
        <p class="page-subtitle">
            Refine resume content using specialized improvement modes while preserving full factual truthfulness.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.active_resume_text.strip():
        st.info("Please load or upload a resume in the left sidebar to use the AI Resume Studio.")
        st.stop()

    bullets_analysis = analyze_bullet_points(st.session_state.active_resume_text)
    candidate_bullets = [b["original_text"] for b in bullets_analysis["analyzed_bullets"]]
    
    col_st_left, col_st_right = st.columns([1, 1.2], gap="large")
    
    with col_st_left:
        st.markdown("""<div class="app-card">
<h4 style="margin:0 0 10px 0; color:#FB7185;">1. Select Content to Refine</h4>
</div>""", unsafe_allow_html=True)
        
        input_source_type = st.radio("Selection Source:", ["From Detected Bullets", "Custom Text Input"], horizontal=True)
        
        if input_source_type == "From Detected Bullets" and candidate_bullets:
            selected_bullet = st.selectbox("Select Resume Bullet Point:", candidate_bullets)
        else:
            selected_bullet = st.text_area("Paste text or bullet point:", value="worked on backend api with database and fixed bugs", height=100)
            
        st.markdown("#### 2. Select Improvement Mode")
        mode = st.selectbox(
            "Improvement Objective:",
            [
                "Apply STAR Framework",
                "Strengthen Action Verbs",
                "Improve Clarity & Conciseness",
                "Align to Target Role Requirements"
            ]
        )
        
        run_improve = st.button("✨ Generate Professional Suggestion", type="primary", use_container_width=True)

    with col_st_right:
        st.markdown("""<div class="app-card">
<h4 style="margin:0 0 10px 0; color:#29D9A0;">3. Side-by-Side Review & Apply</h4>
</div>""", unsafe_allow_html=True)
        
        if run_improve and selected_bullet.strip():
            with st.spinner("Generating truthful professional enhancement..."):
                result = improve_resume_content(
                    original_text=selected_bullet,
                    improvement_mode=mode,
                    target_role=jd_choice,
                    api_key=st.session_state.gemini_api_key
                )
                
                st.session_state.last_studio_result = result
                st.session_state.last_studio_original = selected_bullet
                
        if "last_studio_result" in st.session_state and st.session_state.last_studio_result:
            res = st.session_state.last_studio_result
            orig = st.session_state.get("last_studio_original", "")
            
            st.markdown(f"""
            <div class="editor-diff-grid">
                <div class="diff-panel" style="border-left: 3px solid #64748B;">
                    <div class="diff-header" style="color: var(--text-secondary);">Original Text</div>
                    <div class="diff-text">{orig}</div>
                </div>
                <div class="diff-panel" style="border-left: 3px solid #10B981;">
                    <div class="diff-header" style="color: #10B981;">Suggested Enhancement ({res['engine']})</div>
                    <div class="diff-text">{res['improved_text']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<div style='font-size:0.78rem; color:var(--text-muted); margin: 10px 0;'><b>Rationale:</b> {res['explanation']}</div>", unsafe_allow_html=True)
            
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                st.code(res['improved_text'], language="text")
            with col_act2:
                if st.button("✅ Apply Suggestion to Active Resume", use_container_width=True):
                    if orig in st.session_state.active_resume_text:
                        st.session_state.active_resume_text = st.session_state.active_resume_text.replace(orig, res['improved_text'])
                        st.success("Successfully replaced in active resume!")
                        st.rerun()
                    else:
                        st.warning("Original line was modified or not found directly in document. You can copy the text above.")
        else:
            st.caption("Select a bullet point and click 'Generate Professional Suggestion' to view side-by-side enhancements.")


# ------------------------------------------------------------------------------
# ROUTE 4: MOCK INTERVIEW ROOM (FEATURE FOUR)
# ------------------------------------------------------------------------------
elif st.session_state.workspace_view == "🎙️ Mock Interview Room":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">Mock Interview <span>Room</span></h1>
        <p class="page-subtitle">
            Interactive practice session tailored to your resume experience with real-time feedback and evaluation metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.active_resume_text.strip():
        st.info("Please load or upload a resume in the left sidebar to generate personalized interview questions.")
        st.stop()

    # Session Setup or Active Session
    if not st.session_state.interview_session_active:
        col_setup1, col_setup2 = st.columns([1, 1], gap="large")
        with col_setup1:
            st.markdown("""<div class="app-card">
<h4 style="margin:0 0 12px 0; color:#FB7185;">🎯 Interview Session Parameters</h4>
</div>""", unsafe_allow_html=True)
            
            int_role = st.selectbox("Interview Target Role:", list(sample_jds.keys()), index=0)
            int_type = st.selectbox("Interview Type:", ["Technical Core", "Behavioral & Leadership", "Mixed Comprehensive"])
            int_diff = st.selectbox("Difficulty Level:", ["Intermediate (Standard)", "Beginner (Foundational)", "Advanced (Senior Architecture)"])
            int_count = st.slider("Question Count:", min_value=3, max_value=5, value=3)
            
            if st.button("🚀 Begin Interactive Practice Session", type="primary", use_container_width=True):
                with st.spinner("Formulating personalized interview questions from resume..."):
                    skills_extracted = extract_skills_from_text(st.session_state.active_resume_text)
                    sec_extracted = segment_resume_sections(st.session_state.active_resume_text)
                    proj_text = sec_extracted.get("projects", "") + "\n" + sec_extracted.get("experience", "")
                    
                    q_list = generate_interview_questions(
                        resume_skills=skills_extracted["all_skills"],
                        projects_text=proj_text,
                        target_role=int_role,
                        interview_type=int_type,
                        difficulty=int_diff,
                        question_count=int_count,
                        api_key=st.session_state.gemini_api_key
                    )
                    st.session_state.interview_questions_list = q_list
                    st.session_state.interview_q_index = 0
                    st.session_state.interview_evaluations = []
                    st.session_state.interview_session_active = True
                    st.rerun()

        with col_setup2:
            st.markdown("""<div class="feature-discover-card">
<h4 style="margin:0 0 12px 0; color:var(--text-main);">How Interview Practice Works</h4>
<p style="font-size:0.82rem; color:var(--text-secondary); line-height:1.5;">
• Questions are dynamically formulated using your <b>actual projects and tech stack</b>.<br/>
• Type your verbal or technical response to each question.<br/>
• Receive immediate ratings on <b>Relevance, Technical Accuracy, and Completeness</b> along with stronger model answers.
</p>
</div>""", unsafe_allow_html=True)

    else:
        # Active Practice Room Interface
        q_idx = st.session_state.interview_q_index
        q_list = st.session_state.interview_questions_list
        
        if q_idx < len(q_list):
            curr_q = q_list[q_idx]
            st.markdown(f"""
            <div class="app-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="step-badge">Question {q_idx + 1} of {len(q_list)}</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">{curr_q.get('category', 'Technical')} • {curr_q.get('difficulty', 'Intermediate')}</span>
                </div>
                <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin: 6px 0;">{curr_q['question']}</h3>
                <div style="font-size: 0.78rem; color: #FB7185; margin-top: 4px;">💡 <b>Evaluator Tip:</b> {curr_q.get('tip', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            ans_input = st.text_area("Your Response / Talking Points:", height=130, key=f"q_ans_{q_idx}", placeholder="Explain your architectural decisions, tools used, and outcomes...")
            
            col_q_act1, col_q_act2 = st.columns([1, 1])
            with col_q_act1:
                eval_clicked = st.button("Submit Answer for Evaluation", type="primary", use_container_width=True)
            with col_q_act2:
                if st.button("Exit Practice Session", use_container_width=True):
                    st.session_state.interview_session_active = False
                    st.rerun()
                    
            if eval_clicked and ans_input.strip():
                with st.spinner("Analyzing candidate response clarity, relevance, and accuracy..."):
                    eval_result = evaluate_interview_answer(
                        question=curr_q["question"],
                        candidate_answer=ans_input,
                        target_role=jd_choice,
                        api_key=st.session_state.gemini_api_key
                    )
                    st.session_state.interview_evaluations.append({
                        "question": curr_q["question"],
                        "answer": ans_input,
                        "eval": eval_result
                    })
                    
            # Display Feedback if evaluated
            if len(st.session_state.interview_evaluations) > q_idx:
                feedback = st.session_state.interview_evaluations[q_idx]["eval"]
                st.markdown("---")
                st.markdown("### 📋 Response Feedback")
                
                col_f1, col_f2, col_f3 = st.columns(3)
                col_f1.metric("Relevance Score", f"{feedback['relevance_score']}%")
                col_f2.metric("Technical Accuracy", f"{feedback['technical_accuracy_score']}%")
                col_f3.metric("Completeness", f"{feedback['completeness_score']}%")
                
                st.markdown(f"**Strengths:** {', '.join(feedback.get('strengths', []))}")
                st.markdown(f"**Actionable Tips:** {', '.join(feedback.get('improvement_tips', []))}")
                with st.expander("📖 Study Stronger Model Answer"):
                    st.write(feedback.get("stronger_sample_answer", ""))
                    
                if st.button("Next Question ➔", type="primary"):
                    st.session_state.interview_q_index += 1
                    st.rerun()
        else:
            # Interview Completed Summary
            st.success("🎉 Practice Session Complete!")
            st.markdown("### 🏆 Session Summary Scorecard")
            evals = st.session_state.interview_evaluations
            if evals:
                avg_rating = round(sum(e["eval"]["overall_rating"] for e in evals) / len(evals), 1)
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 16px;">
                    <div class="kpi-title">Average Practice Performance</div>
                    <div class="kpi-value" style="color: #10B981;">{avg_rating}%</div>
                    <div class="kpi-desc">Across {len(evals)} Interview Questions Evaluated</div>
                </div>
                """, unsafe_allow_html=True)
                
            if st.button("Restart New Practice Session", type="primary"):
                st.session_state.interview_session_active = False
                st.rerun()


# ------------------------------------------------------------------------------
# ROUTE 5: ANALYSIS HISTORY (FEATURE TWO)
# ------------------------------------------------------------------------------
elif st.session_state.workspace_view == "📜 Analysis History":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">Analysis <span>History</span></h1>
        <p class="page-subtitle">
            Review, restore, or export previous resume audit sessions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    records = get_all_history()
    
    if records:
        st.markdown(f"**Saved Session Records ({len(records)}):**")
        for r in records:
            col_h1, col_h2, col_h3, col_h4 = st.columns([2, 1.5, 1, 1.2])
            with col_h1:
                st.markdown(f"**{r.get('resume_name', 'Resume')}** ({r.get('candidate_name', 'Applicant')})")
                st.caption(f"Role: {r.get('target_role', 'Software Engineer')} • Date: {r.get('timestamp', '')}")
            with col_h2:
                st.markdown(f"Score: **{r.get('ats_score', 0)}/100**")
                st.caption(f"Skills: {r.get('skills_count', 0)} ({r.get('matched_skills_count', 0)} matched)")
            with col_h3:
                if st.button("Restore", key=f"rest_{r['id']}", use_container_width=True):
                    if r.get("full_text"):
                        st.session_state.active_resume_text = r["full_text"]
                        st.session_state.active_file_name = r.get("resume_name", "")
                        st.session_state.workspace_view = "📑 Resume Analyzer"
                        st.success("Restored to active workspace!")
                        st.rerun()
            with col_h4:
                if st.button("Delete", key=f"del_{r['id']}", use_container_width=True):
                    delete_history_record(r['id'])
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: var(--border-subtle);'/>", unsafe_allow_html=True)
    else:
        st.info("No saved analysis records found. Analyze a resume in the Resume Analyzer to automatically record session history!")


# ------------------------------------------------------------------------------
# ROUTE 6: AUTHENTICATION & USER PROFILE
# ------------------------------------------------------------------------------
elif st.session_state.workspace_view == "🔑 Login / Account":
    st.markdown("""
    <div class="page-header-container">
        <h1 class="page-title">User <span>Authentication</span></h1>
        <p class="page-subtitle">
            Sign in or create your credentials to upload resumes, unlock ATS evaluation engines, and personalize career reports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("auth_notice"):
        st.warning(f"🔒 {st.session_state.auth_notice}")
        st.session_state.auth_notice = ""
        
    if not st.session_state.get("is_logged_in", False):
        col_space_l, col_auth_box, col_space_r = st.columns([1, 2.2, 1])
        with col_auth_box:
            st.markdown("""
            <div class="auth-card-wrapper">
                <div class="auth-avatar-banner">⚡</div>
                <h2 style="text-align: center; font-size: 1.35rem; font-weight: 800; margin-bottom: 4px; color: var(--text-main);">
                    Welcome to AI Resume Analyzer
                </h2>
                <p style="text-align: center; font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 20px;">
                    Enter your name and credentials to get started
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            auth_tab_login, auth_tab_reg, auth_tab_demo = st.tabs(["🔑 Sign In", "✨ Create Account", "⚡ Quick Demo"])
            
            with auth_tab_login:
                st.markdown("<p style='font-size:0.84rem; color:var(--text-secondary); margin-top:8px;'>Enter your registered username and password to log in.</p>", unsafe_allow_html=True)
                with st.form("login_form", clear_on_submit=False):
                    login_user = st.text_input("Username", placeholder="e.g. alexmorgan, @alex, or alex@email.com", key="input_login_username")
                    login_pass = st.text_input("Password", type="password", placeholder="••••••••", key="input_login_password")
                    btn_submit_login = st.form_submit_button("Sign In to AI Resume Analyzer", type="primary", use_container_width=True)
                    
                    if btn_submit_login:
                        if not login_user or not login_pass:
                            st.error("Please fill in both username and password.")
                        else:
                            success, msg, user_obj = authenticate_user(login_user, login_pass)
                            if success and user_obj:
                                sess_token = create_user_session(user_obj.get("username", login_user))
                                st.query_params["session"] = sess_token
                                st.session_state.is_logged_in = True
                                st.session_state.session_token = sess_token
                                st.session_state.user_name = user_obj.get("name", login_user)
                                st.session_state.username = user_obj.get("username", login_user)
                                st.session_state.workspace_view = "📑 Resume Analyzer"
                                st.success(f"Welcome back, {user_obj.get('name')}!")
                                st.rerun()
                            else:
                                st.error(msg)
                                
            with auth_tab_reg:
                st.markdown("<p style='font-size:0.84rem; color:var(--text-secondary); margin-top:8px;'>Create your account. Your name will be displayed in the app and on generated reports.</p>", unsafe_allow_html=True)
                with st.form("register_form", clear_on_submit=False):
                    reg_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan", help="This name will appear on the top right, in greetings, and on ATS audit reports.")
                    reg_user = st.text_input("Username", placeholder="e.g. alexmorgan, @alex, or alex@email.com (letters, numbers, @, ., _, -)")
                    reg_pass = st.text_input("Password", type="password", placeholder="At least 4 characters")
                    reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                    btn_submit_reg = st.form_submit_button("Create Account & Sign In", type="primary", use_container_width=True)
                    
                    if btn_submit_reg:
                        if not reg_name or not reg_user or not reg_pass:
                            st.error("All fields are required. Please enter your full name, username, and password.")
                        elif reg_pass != reg_confirm:
                            st.error("Passwords do not match. Please verify your password confirmation.")
                        else:
                            success, msg, user_obj = register_user(reg_name, reg_user, reg_pass)
                            if success and user_obj:
                                sess_token = create_user_session(user_obj.get("username", reg_user))
                                st.query_params["session"] = sess_token
                                st.session_state.is_logged_in = True
                                st.session_state.session_token = sess_token
                                st.session_state.user_name = user_obj.get("name", reg_name)
                                st.session_state.username = user_obj.get("username", reg_user)
                                st.session_state.workspace_view = "📑 Resume Analyzer"
                                st.success(f"Account created successfully! Welcome, {user_obj.get('name')}!")
                                st.rerun()
                            else:
                                st.error(msg)
                                
            with auth_tab_demo:
                st.markdown("""
                <div style="background: var(--surface-card); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 14px; margin-top: 10px;">
                    <div style="font-weight: 700; font-size: 0.90rem; color: var(--text-main); margin-bottom: 4px;">⚡ Instant Academic / Viva Demo Access</div>
                    <div style="font-size: 0.80rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 12px;">
                        Quickly explore without manual typing using the default demo candidate profile.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Sign In as Demo User (Alex Morgan)", use_container_width=True, type="primary"):
                    sess_token = create_user_session("alex_demo")
                    st.query_params["session"] = sess_token
                    st.session_state.is_logged_in = True
                    st.session_state.session_token = sess_token
                    st.session_state.user_name = "Alex Morgan"
                    st.session_state.username = "alex_demo"
                    st.session_state.workspace_view = "📑 Resume Analyzer"
                    st.rerun()
                    
    else:
        # User is already logged in - show clean Profile & Session Management Card
        col_space_l, col_profile_box, col_space_r = st.columns([1, 2.2, 1])
        with col_profile_box:
            user_handle = st.session_state.username if ("@" in st.session_state.username) else f"@{st.session_state.username}"
            st.markdown(f"""<div class="hero-upload-card" style="padding: 24px; margin-bottom: 18px;">
<div style="display: flex; align-items: center; gap: 16px;">
<div class="brand-logo" style="width: 52px; height: 52px; font-size: 26px; border-radius: 14px;">👤</div>
<div>
<div style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); line-height: 1.2;">
{st.session_state.user_name}
</div>
<div style="font-size: 0.85rem; color: var(--color-accent-pink); font-weight: 600;">
{user_handle}
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if st.button("📑 Return to Resume Analyzer", type="primary", use_container_width=True):
                    st.session_state.workspace_view = "📑 Resume Analyzer"
                    st.rerun()
            with col_a2:
                if st.button("🚪 Sign Out of AI Resume Analyzer", use_container_width=True):
                    if st.session_state.get("session_token"):
                        destroy_user_session(st.session_state.session_token)
                    st.session_state.is_logged_in = False
                    st.session_state.user_name = ""
                    st.session_state.username = ""
                    st.session_state.session_token = ""
                    if "session" in st.query_params:
                        del st.query_params["session"]
                    st.rerun()
