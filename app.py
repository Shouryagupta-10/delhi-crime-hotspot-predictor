"""
Rakshak.ai: Delhi Crime Hotspot & Safe-Route Navigator
Production-grade Civic Intelligence & Spatial Navigation System
Linear / Dark Sky Dispatch Style Interface
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

# Set Streamlit page config as first command
st.set_page_config(
    page_title="Rakshak.ai | Delhi Safe Route Navigator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Local imports
from config import (
    GOOGLE_MAPS_API_KEY,
    DELHI_CENTER,
    DELHI_LANDMARKS,
    DEFAULT_ALERT_BUFFER_METERS,
    THEME
)
from data_loader import load_and_cluster_crime_data
from router import RoutePlanner
from components.map_view import render_rakshak_map

# -----------------------------------------------------------------------------
# STRICT ANTI-SLOP DISPATCH CSS (Dark Sky / Linear Palette)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Base */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #090d16 !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif !important;
    }
    
    /* Clean Streamlit Header & Clutter Removal */
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(8px) !important;
        height: 2.5rem !important;
    }
    .stDeployButton, #MainMenu, footer {
        visibility: hidden !important;
        display: none !important;
    }
    [data-testid="stToolbar"] {
        right: 1.5rem !important;
    }
    
    /* Sidebar Drawer (Dark Dispatch Control Panel) */
    [data-testid="stSidebar"] {
        background-color: #0c121e !important;
        border-right: 1px solid #1e293b !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.85rem !important;
        padding-top: 1rem !important;
    }
    
    /* Main Content Padding (Maximize Map Area) */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Top Status Bar Pill */
    .top-status-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 8px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(12px);
    }
    .status-left {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
        letter-spacing: 0.04em;
        font-weight: 600;
        color: #94a3b8;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #064e3b;
        color: #34d399;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 700;
    }
    .status-right {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 11px;
        color: #64748b;
    }

    /* Form Controls: Selectbox, Inputs & Sliders */
    .stSelectbox label, .stTextInput label, .stSlider label {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        color: #f8fafc !important;
        font-size: 13px !important;
    }
    div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        color: #f8fafc !important;
    }
    input {
        color: #f8fafc !important;
        font-size: 13px !important;
    }

    /* Dispatch Action Button */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        padding: 10px 16px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(180deg, #0369a1 0%, #075985 100%) !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* Linear Metric Cards */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .metric-card.highlight {
        border-color: #06b6d4;
        background: rgba(6, 182, 212, 0.06);
    }
    .metric-card.hazard {
        border-color: #ef4444;
        background: rgba(239, 68, 68, 0.06);
    }
    .metric-title {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: 4px;
    }

    /* Hazard Inspection Drawer */
    .hazard-item {
        background: #171c28;
        border-left: 3px solid #ef4444;
        border-radius: 0 6px 6px 0;
        padding: 8px 12px;
        margin-bottom: 6px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA CACHING & INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_clustered_dataset():
    """Caches CSV ingestion and Haversine DBSCAN clustering."""
    return load_and_cluster_crime_data(
        filepath="data/delhi_crime_records.csv",
        eps_km=0.75,
        min_samples=8
    )

with st.spinner("Ingesting Delhi FIR records and executing DBSCAN spatial clustering..."):
    df, hotspots, safe_zones = get_clustered_dataset()

critical_count = sum(1 for h in hotspots if h["is_critical"])
warning_count = sum(1 for h in hotspots if not h["is_critical"])


# -----------------------------------------------------------------------------
# TOP STATUS PILL (Subtle System Readiness)
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="top-status-bar">
    <div class="status-left">
        <span class="status-badge">🟢 RADAR OPERATIONAL</span>
        <span style="color: #f8fafc; font-weight: 700;">RAKSHAK.AI</span>
        <span style="color: #64748b;">|</span>
        <span>DELHI NCT CIVIC INTELLIGENCE</span>
        <span style="color: #64748b;">|</span>
        <span style="color: #cbd5e1;">DBSCAN CLUSTERS: <strong style="color: #f87171;">{critical_count} CRITICAL</strong> / <strong style="color: #fbbf24;">{warning_count} WARNING</strong></span>
    </div>
    <div class="status-right">
        RECORDS: {len(df):,} FIRs | BUFFER: {DEFAULT_ALERT_BUFFER_METERS}M | AUDIO: SYNTHESIZED
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR CONTROL DRAWER
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.02em; color: #f8fafc;">
            🛡️ RAKSHAK.AI
        </div>
        <div style="font-size: 11px; color: #94a3b8; font-weight: 500;">
            Delhi Crime Hotspot & Safe-Route Navigator
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Route Origin Input
    landmark_names = list(DELHI_LANDMARKS.keys())
    
    origin_choice = st.selectbox(
        "📍 Starting Point (Origin)",
        options=["My Current Location (GPS Auto-Detect)"] + landmark_names,
        index=1  # Default to Connaught Place
    )

    # Route Destination Input
    dest_choice = st.selectbox(
        "🏁 Destination",
        options=landmark_names,
        index=1  # Default to Hauz Khas Village
    )

    # Route Display Mode
    route_mode = st.selectbox(
        "Routing Mode",
        options=["Both (Standard vs Safest Comparison)", "Safest Route (DBSCAN Avoidance)", "Standard Route (Direct Fastest)"],
        index=0
    )

    mode_map = {
        "Both (Standard vs Safest Comparison)": "both",
        "Safest Route (DBSCAN Avoidance)": "safest",
        "Standard Route (Direct Fastest)": "standard"
    }
    active_mode = mode_map[route_mode]

    # Proximity Alert Buffer Slider
    buffer_meters = st.slider(
        "Hazard Warning Radius (Meters)",
        min_value=150,
        max_value=800,
        value=DEFAULT_ALERT_BUFFER_METERS,
        step=50,
        help="Audio alert and banner trigger when route comes within this distance of any critical hotspot perimeter."
    )

    # Calculate Route Action
    calc_button = st.button("Calculate Safe Corridor ⚡")

    st.markdown("---")

    # Routing Execution
    router = RoutePlanner(api_key=GOOGLE_MAPS_API_KEY)
    
    # Resolve Origin (GPS Auto-detect resolves to Connaught Place as baseline anchor)
    if "GPS" in origin_choice:
        origin_coord = DELHI_CENTER
    else:
        origin_coord = DELHI_LANDMARKS.get(origin_choice, DELHI_CENTER)
        
    dest_coord = DELHI_LANDMARKS.get(dest_choice, DELHI_LANDMARKS["Hauz Khas Village & Social"])

    # Calculate safe routing
    route_result = router.plan_safe_route(
        origin_input=origin_coord,
        destination_input=dest_coord,
        hotspots=hotspots,
        buffer_meters=buffer_meters
    )

    std_route = route_result["standard"]
    safe_route = route_result["safest"]

    # Comparative Metric Cards (Linear Dispatch Style)
    st.markdown('<div style="font-size:11px; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:6px;">Route Safety Comparison</div>', unsafe_allow_html=True)
    
    # Safest Route Card
    safe_breaches_count = len(safe_route["breaches"])
    st.markdown(f"""
    <div class="metric-card highlight">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="metric-title" style="color: #38bdf8;">🛡️ Safest Corridor</div>
            <span style="font-size: 10px; background: #064e3b; color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: 700;">RECOMMENDED</span>
        </div>
        <div class="metric-value">{safe_route['safety_score']}% <span style="font-size:12px; font-weight:500; color:#38bdf8;">Safety Index</span></div>
        <div class="metric-sub">
            Distance: <strong>{safe_route['distance_km']} km</strong> &nbsp;|&nbsp; Est: <strong>{safe_route['duration_min']} min</strong><br/>
            Critical Breaches: <strong style="color: {'#34d399' if safe_breaches_count == 0 else '#fbbf24'};">{safe_breaches_count} zone{'s' if safe_breaches_count != 1 else ''}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Standard Route Card
    std_breaches_count = len(std_route["breaches"])
    st.markdown(f"""
    <div class="metric-card hazard">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="metric-title" style="color: #f87171;">⚠️ Standard Direct Path</div>
            <span style="font-size: 10px; background: #7f1d1d; color: #fecaca; padding: 2px 6px; border-radius: 4px; font-weight: 700;">EXPOSURE</span>
        </div>
        <div class="metric-value">{std_route['safety_score']}% <span style="font-size:12px; font-weight:500; color:#f87171;">Safety Index</span></div>
        <div class="metric-sub">
            Distance: <strong>{std_route['distance_km']} km</strong> &nbsp;|&nbsp; Est: <strong>{std_route['duration_min']} min</strong><br/>
            Critical Breaches: <strong style="color: #ef4444;">{std_breaches_count} zone{'s' if std_breaches_count != 1 else ''}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Breached Hotspot Details
    if std_route["breaches"]:
        st.markdown('<div style="font-size:11px; font-weight:700; color:#ef4444; text-transform:uppercase; margin-top:10px; margin-bottom:6px;">⚠️ Hazards on Direct Path:</div>', unsafe_allow_html=True)
        for b in std_route["breaches"][:3]:
            st.markdown(f"""
            <div class="hazard-item">
                <strong style="color:#f8fafc;">{b['hotspot_name']}</strong><br/>
                <span style="color:#94a3b8;">Proximity: {b['min_distance_meters']}m &bull; Crime: {b['dominant_crime']} &bull; Incidents: {b['incident_count']}</span>
            </div>
            """, unsafe_allow_html=True)

    # Developer Note for Dataset Swap
    with st.expander("ℹ️ Data Architecture & 10-Year Dataset Swap"):
        st.markdown("""
        **To swap with your 10-year historical dataset:**
        1. Replace `data/delhi_crime_records.csv` with your full FIR dataset.
        2. Required columns: `latitude`, `longitude`.
        3. Optional rich columns: `crime_category`, `severity_score`, `landmark_premise`, `district`.
        4. Clustering automatically adjusts density thresholds based on incident distributions.
        """)


# -----------------------------------------------------------------------------
# MAIN VIEW: INTERACTIVE MAP CANVAS & WEB AUDIO RADAR
# -----------------------------------------------------------------------------
render_rakshak_map(
    google_api_key=GOOGLE_MAPS_API_KEY,
    center=origin_coord,
    zoom=12,
    hotspots=hotspots,
    safe_zones=safe_zones,
    standard_route=std_route,
    safest_route=safe_route,
    active_route_type=active_mode,
    alert_buffer_meters=buffer_meters,
    height=740
)
