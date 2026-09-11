#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "========================================================"
echo "🛡️  Rakshak.ai — Starting Backend & Predictive Policing"
echo "========================================================"

if [ -f "../.venv/bin/activate" ]; then
    source "../.venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
fi

python3 -m streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
