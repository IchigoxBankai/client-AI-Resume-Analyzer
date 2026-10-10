#!/bin/bash
echo "========================================================"
echo "      ResuMetric AI - Resume Analyzer & Career Suite"
echo "      BSc Computer Science Final Year Project"
echo "========================================================"
echo ""
echo "[1/2] Checking Python..."
python3 --version || python --version
echo ""
echo "[2/2] Starting Streamlit Server..."
streamlit run app.py
