# Rakshak.ai — Backend & ML Intelligence Engine

Comprehensive backend architecture powering **predictive policing**, **spatial clustering (DBSCAN)**, **supervised crime risk prediction (XGBoost)**, and **x402 micro-payment settlement on Algorand**.

---

## 🚀 Quick Start

From this directory (`backend/`):

```bash
# 1. Activate Python virtual environment & install requirements
source ../.venv/bin/activate
pip install -r requirements.txt

# 2. Launch the Streamlit Predictive Policing & Geospatial Dashboard
./run_backend.sh
# or: streamlit run app/main.py
```

The backend dashboard will launch at `http://localhost:8501`.

To launch the **Node.js x402 Micropayment Server**:
```bash
cd x402-server
npm install
node server.js
```
The x402 server runs on `http://localhost:4020`.

---

## 📂 Directory Structure

- `models/`:
  - `predictive_policing.py`: Patrol beat optimizer (Koper curve 12-15m rule), Knox near-repeat space-time contagion engine, safest corridor router, and tactical barricade planner.
  - `cluster_engine.py`: Haversine DBSCAN & K-Means density clustering.
  - `risk_predictor.py`: Gradient Boosted crime severity and risk classifier.
  - `saved_models.pkl`: Serialized model pipeline bundle.
- `app/`:
  - `main.py`: Interactive Streamlit application.
  - `map_renderer.py`: Folium geospatial map renderer.
- `../data/` (Project Root Data):
  - `delhi_crime_records.csv`: 18,468 verified Delhi crime incidents across 15 districts (2015–2026).
  - `raw_delhi_police_reports.csv`: 25,375 raw police incident logs.
  - `generate_delhi_data.py`: Dataset generator with grounded Delhi coordinates.
  - `cleaner.py`: 6-stage FIR verification and data cleaning pipeline.
- `x402-server/`:
  - `server.js`: Express server returning HTTP 402 Payment Required for enterprise API calls and verifying Algorand Testnet transactions.
- `tests/`:
  - `test_pipeline.py`: Automated test suite for data validation and model inference.
