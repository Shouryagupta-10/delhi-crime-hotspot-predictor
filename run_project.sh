#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  🗺️ DELHI CRIME HOTSPOT & PREMISES RISK PREDICTOR 🚨     "
echo "  Geospatial AI & Haversine DBSCAN Hotspot Studio          "
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv --system-site-packages .venv
    .venv/bin/pip install -r requirements.txt
fi

if [ ! -f "data/delhi_crime_records.csv" ]; then
    echo "Generating Delhi premises crime dataset..."
    .venv/bin/python data/generate_delhi_data.py
fi

if [ ! -f "models/saved_models.pkl" ]; then
    echo "Training supervised risk predictor and clustering engine..."
    .venv/bin/python -m models.risk_predictor
fi

echo "Running verification test suite..."
.venv/bin/python tests/test_pipeline.py

echo ""
echo "🚀 Launching Streamlit Interactive Dashboard on http://localhost:8501..."
HOME="$DIR" .venv/bin/python -m streamlit run app/main.py
