@echo off
title AI Resume Analyzer - Resume Analyzer
echo ========================================================
echo       AI Resume Analyzer - Resume Analyzer & Career Suite
echo       BSc Computer Science Final Year Project
echo ========================================================
echo.
echo [1/2] Checking Python environment...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    pause
    exit /b
)

echo.
echo [2/2] Launching AI Resume Analyzer Streamlit Server...
echo Opening in default browser at http://localhost:8501
streamlit run app.py
pause
