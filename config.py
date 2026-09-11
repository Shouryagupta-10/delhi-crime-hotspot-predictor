"""
Rakshak.ai Configuration Module
Defines runtime configurations, environment keys, Delhi geospatial bounds,
clustering thresholds, and design system constants.
"""

import os
from typing import Dict, Tuple, Any

# Google Maps API Key ingestion (supports environment variable and Streamlit secrets)
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

# Fallback check for Streamlit secrets without crashing if streamlit is imported
try:
    import streamlit as st
    if not GOOGLE_MAPS_API_KEY and hasattr(st, "secrets") and "GOOGLE_MAPS_API_KEY" in st.secrets:
        GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except Exception:
    pass

# Delhi National Capital Territory (NCT) Bounding Box and Center
DELHI_CENTER: Tuple[float, float] = (28.6315, 77.2167)  # Connaught Place Central Hub
DELHI_DEFAULT_ZOOM = 12

DELHI_BOUNDS = {
    "lat_min": 28.30,
    "lat_max": 28.95,
    "lon_min": 76.80,
    "lon_max": 77.50
}

# Standard Delhi Landmark Pre-sets for Rapid Routing and Prototyping
DELHI_LANDMARKS: Dict[str, Tuple[float, float]] = {
    "Connaught Place (Inner Circle)": (28.6315, 77.2167),
    "Hauz Khas Village & Social": (28.5494, 77.1994),
    "Saket District Centre & Select Citywalk": (28.5284, 77.2185),
    "Chandni Chowk / Red Fort (Old Delhi)": (28.6506, 77.2303),
    "Rohini Sector 10 / Swarn Jayanti Park": (28.7118, 77.1190),
    "India Gate & Kartavya Path": (28.6129, 77.2295),
    "Dwarka Sector 14 Metro Interchange": (28.5921, 77.0315),
    "Karol Bagh Gaffar Market": (28.6514, 77.1907),
    "Anand Vihar ISBT Terminal": (28.6477, 77.3161),
    "Delhi University North Campus (Arts Faculty)": (28.6907, 77.2066),
    "Lajpat Nagar Central Market": (28.5677, 77.2433),
    "Vasant Kunj Promenade Mall": (28.5387, 77.1586),
    "Punjabi Bagh Club Road": (28.6689, 77.1308),
    "Laxmi Nagar Vikas Marg Market": (28.6319, 77.2777),
    "New Delhi Railway Station (NDLS Gate 2)": (28.6445, 77.2206),
    "Janakpuri District Centre": (28.6291, 77.0818),
    "Cyber Hub Border (NH48 Toll Plaza)": (28.4986, 77.0878),
    "Noida Sector 18 Border (DND Flyway)": (28.5708, 77.3260)
}

# Clustering & Algorithmic Parameters
DBSCAN_EPS_KM: float = 0.75          # Radius of neighborhood in km (~750m)
DBSCAN_MIN_SAMPLES: int = 8          # Minimum crime reports to classify as a cluster
EARTH_RADIUS_KM: float = 6371.0088   # WGS-84 Mean Earth Radius in km

# Proximity Audio Alert Threshold
DEFAULT_ALERT_BUFFER_METERS: int = 300  # Distance in meters from critical hotspot boundary to trigger alert
SIMULATION_SPEED_MS: int = 250          # Interval between route coordinate simulation steps

# Visual & Theme System (Dark Sky / Linear Dispatch Palette)
THEME = {
    "bg_base": "#090d16",
    "card_bg": "#0f172a",
    "card_border": "#1e293b",
    "text_heading": "#f8fafc",
    "text_body": "#cbd5e1",
    "text_muted": "#64748b",
    "hazard_red": "#ef4444",       # Critical Hotspot
    "hazard_red_fill": "rgba(239, 68, 68, 0.28)",
    "warning_amber": "#f59e0b",    # Warning Buffer Zone
    "warning_amber_fill": "rgba(245, 158, 11, 0.18)",
    "safe_green": "#10b981",       # Safe Patrol Corridor
    "safe_green_fill": "rgba(16, 185, 129, 0.14)",
    "route_standard": "#f43f5e",   # Red/Rose line (passes through hotspots)
    "route_safe": "#06b6d4",       # Luminous Cyan (detours around hotspots)
    "beacon_blue": "#38bdf8"
}
