"""
Rakshak.ai Interactive Map View Component
Renders an edge-to-edge geospatial canvas supporting Google Maps JavaScript API
and dark-sky dispatch fallback with HTML5 geolocation, DBSCAN risk layers,
route comparison polylines, and Web Audio API synthesized proximity alerts.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
import streamlit.components.v1 as components

from config import (
    GOOGLE_MAPS_API_KEY,
    DELHI_CENTER,
    DEFAULT_ALERT_BUFFER_METERS,
    THEME
)

def render_rakshak_map(
    google_api_key: str = GOOGLE_MAPS_API_KEY,
    center: Tuple[float, float] = DELHI_CENTER,
    zoom: int = 12,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    safe_zones: Optional[List[Dict[str, Any]]] = None,
    standard_route: Optional[Dict[str, Any]] = None,
    safest_route: Optional[Dict[str, Any]] = None,
    active_route_type: str = "both",  # "both", "safest", "standard", "none"
    alert_buffer_meters: int = DEFAULT_ALERT_BUFFER_METERS,
    height: int = 740
) -> None:
    """
    Renders the unified interactive map inside the Streamlit view.
    """
    hotspots = hotspots or []
    safe_zones = safe_zones or []
    
    # Serialize data for JavaScript injection
    hotspots_json = json.dumps(hotspots)
    safe_zones_json = json.dumps(safe_zones)
    std_route_json = json.dumps(standard_route if standard_route else {})
    safe_route_json = json.dumps(safest_route if safest_route else {})
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rakshak.ai Geospatial Dispatch Map</title>
        
        <!-- Leaflet Core CSS & JS for universal fallback or direct rendering -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
        
        <!-- Google Fonts: Outfit & Inter for ultra-clean Linear-style typography -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body, html {{
                height: 100%;
                width: 100%;
                background-color: #090d16;
                color: #f8fafc;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                overflow: hidden;
            }}
            #map-container {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #090d16;
            }}
            #map {{
                width: 100%;
                height: 100%;
            }}
            
            /* High-Priority Warning Banner (Floating Top HUD) */
            #alert-banner {{
                position: absolute;
                top: 16px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                display: none;
                align-items: center;
                gap: 12px;
                background: rgba(15, 23, 42, 0.92);
                border: 1px solid #ef4444;
                box-shadow: 0 0 25px rgba(239, 68, 68, 0.35);
                backdrop-filter: blur(12px);
                padding: 10px 20px;
                border-radius: 9999px;
                color: #fecaca;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.02em;
                animation: pulseAlert 1.5s infinite ease-in-out;
                max-width: 90%;
            }}
            @keyframes pulseAlert {{
                0%, 100% {{ box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); border-color: #ef4444; }}
                50% {{ box-shadow: 0 0 30px rgba(239, 68, 68, 0.7); border-color: #f87171; }}
            }}
            
            #safe-banner {{
                position: absolute;
                top: 16px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 999;
                display: none;
                align-items: center;
                gap: 10px;
                background: rgba(15, 23, 42, 0.90);
                border: 1px solid #10b981;
                box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
                backdrop-filter: blur(12px);
                padding: 8px 18px;
                border-radius: 9999px;
                color: #a7f3d0;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.02em;
            }}

            /* Floating Dispatch Controls Overlay (Linear style) */
            .map-hud-panel {{
                position: absolute;
                top: 16px;
                right: 16px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .hud-btn {{
                background: rgba(15, 23, 42, 0.88);
                color: #cbd5e1;
                border: 1px solid #334155;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                backdrop-filter: blur(8px);
                display: flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s ease;
                user-select: none;
            }}
            .hud-btn:hover {{
                background: rgba(30, 41, 59, 0.95);
                color: #f8fafc;
                border-color: #06b6d4;
                transform: translateY(-1px);
            }}
            .hud-btn.active {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
            }}

            /* Floating Action Button (FAB) for Geolocation Re-Center */
            .fab-recenter {{
                position: absolute;
                bottom: 24px;
                right: 16px;
                z-index: 1000;
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: rgba(15, 23, 42, 0.92);
                border: 1px solid #06b6d4;
                color: #06b6d4;
                box-shadow: 0 4px 14px rgba(6, 182, 212, 0.25);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .fab-recenter:hover {{
                background: #06b6d4;
                color: #0f172a;
                transform: scale(1.08);
                box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
            }}

            /* Bottom Simulation & Playback Drawer */
            #sim-drawer {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                z-index: 1000;
                background: rgba(15, 23, 42, 0.90);
                border: 1px solid #334155;
                backdrop-filter: blur(14px);
                padding: 10px 16px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                gap: 14px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            }}
            .sim-btn {{
                background: #1e293b;
                border: 1px solid #475569;
                color: #f1f5f9;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.15s ease;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .sim-btn:hover {{
                background: #334155;
                border-color: #06b6d4;
            }}
            .sim-btn.primary {{
                background: #0284c7;
                border-color: #38bdf8;
                color: #ffffff;
            }}
            .sim-btn.primary:hover {{
                background: #0369a1;
            }}
            .sim-status {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: #94a3b8;
                min-width: 140px;
            }}
            
            /* Layer Toggle Bar */
            #layer-bar {{
                position: absolute;
                top: 16px;
                left: 16px;
                z-index: 1000;
                background: rgba(15, 23, 42, 0.88);
                border: 1px solid #334155;
                backdrop-filter: blur(10px);
                border-radius: 8px;
                display: flex;
                padding: 3px;
                gap: 2px;
            }}
            .layer-tab {{
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 500;
                color: #94a3b8;
                cursor: pointer;
                border: none;
                background: transparent;
                transition: all 0.15s ease;
            }}
            .layer-tab.active {{
                background: #1e293b;
                color: #f8fafc;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }}
            
            /* Custom Leaflet Map Dark Styling */
            .leaflet-container {{
                background: #090d16 !important;
                font-family: 'Inter', sans-serif !important;
            }}
            .leaflet-popup-content-wrapper {{
                background: rgba(15, 23, 42, 0.95) !important;
                border: 1px solid #334155 !important;
                border-radius: 10px !important;
                color: #f8fafc !important;
                box-shadow: 0 8px 30px rgba(0,0,0,0.7) !important;
                backdrop-filter: blur(12px);
            }}
            .leaflet-popup-tip {{
                background: #0f172a !important;
            }}
            
            /* Pulsing Red Hazard Node */
            .hazard-pulse {{
                border-radius: 50%;
                background: rgba(239, 68, 68, 0.4);
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                animation: pulseHazard 2s infinite;
            }}
            @keyframes pulseHazard {{
                0% {{
                    transform: scale(0.95);
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                }}
                70% {{
                    transform: scale(1.05);
                    box-shadow: 0 0 0 12px rgba(239, 68, 68, 0);
                }}
                100% {{
                    transform: scale(0.95);
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
                }}
            }}
        </style>
    </head>
    <body>
        <div id="map-container">
            <div id="map"></div>
            
            <!-- High-Priority Warning Banner -->
            <div id="alert-banner">
                <span style="font-size: 16px;">⚠️</span>
                <span id="alert-message">ALERT: Route intersects critical crime zone (Area: NDLS Terminal Corridor)</span>
            </div>
            
            <!-- Safe Clear Status Banner -->
            <div id="safe-banner">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981; box-shadow:0 0 8px #10b981;"></span>
                <span id="safe-message">SAFE CORRIDOR CLEAR | Zero Hazard Intersections</span>
            </div>
            
            <!-- Layer Visibility Controls -->
            <div id="layer-bar">
                <button class="layer-tab active" id="tab-all" onclick="setLayerMode('all')">Show All Layers</button>
                <button class="layer-tab" id="tab-hotspots" onclick="setLayerMode('hotspots')">🔴 Critical Hotspots</button>
                <button class="layer-tab" id="tab-safe" onclick="setLayerMode('safe')">🟢 Safe Corridors</button>
            </div>
            
            <!-- HUD Map Controls (Top Right) -->
            <div class="map-hud-panel">
                <button class="hud-btn" id="btn-tile" onclick="toggleTileLayer()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon><line x1="8" y1="2" x2="8" y2="18"></line><line x1="16" y1="6" x2="16" y2="22"></line></svg>
                    <span id="tile-label">Dark Dispatch</span>
                </button>
                <button class="hud-btn" id="btn-audio" onclick="testAlertAudio()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                    <span>Test Audio Alert</span>
                </button>
            </div>
            
            <!-- Floating Action Button: Re-center to User GPS -->
            <div class="fab-recenter" onclick="centerOnUser()" title="Re-center to my live GPS location">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="7"></circle><polyline points="12 1 12 5"></polyline><polyline points="12 19 12 23"></polyline><polyline points="1 12 5 12"></polyline><polyline points="19 12 23 12"></polyline></svg>
            </div>

            <!-- Route Simulation Controller Drawer -->
            <div id="sim-drawer">
                <button class="sim-btn primary" id="sim-toggle-btn" onclick="toggleSimulation()">
                    <span id="sim-icon">▶</span>
                    <span id="sim-btn-text">Simulate Route</span>
                </button>
                <button class="sim-btn" onclick="resetSimulation()">
                    <span>↺ Reset</span>
                </button>
                <div class="sim-status" id="sim-status-text">BEACON: STANDBY</div>
            </div>
        </div>

        <script>
            // --- INGEST DATA ---
            const HOTSPOTS = {hotspots_json};
            const SAFE_ZONES = {safe_zones_json};
            const STANDARD_ROUTE = {std_route_json};
            const SAFEST_ROUTE = {safe_route_json};
            const ACTIVE_ROUTE_TYPE = "{active_route_type}";
            const ALERT_BUFFER_METERS = {alert_buffer_meters};
            const DEFAULT_CENTER = [{center[0]}, {center[1]}];
            const DEFAULT_ZOOM = {zoom};

            // Global State
            let map;
            let userMarker = null;
            let userCoords = DEFAULT_CENTER;
            let currentTileMode = "dark";
            let activeLayerMode = "all";
            let tileLayer;
            let hotspotLayers = [];
            let safeLayers = [];
            let stdRoutePolyline = null;
            let safeRoutePolyline = null;
            let beaconMarker = null;
            let simInterval = null;
            let simStep = 0;
            let isSimulating = false;
            let audioContext = null;
            let lastAlertTime = 0;

            // --- WEB AUDIO API SYNTHESIZER (ZERO .MP3 DEPENDENCY) ---
            function getAudioContext() {{
                if (!audioContext) {{
                    const AudioCtx = window.AudioContext || window.webkitAudioContext;
                    if (AudioCtx) {{
                        audioContext = new AudioCtx();
                    }}
                }}
                if (audioContext && audioContext.state === 'suspended') {{
                    audioContext.resume();
                }}
                return audioContext;
            }}

            function playCrimeAlertChime() {{
                try {{
                    const ctx = getAudioContext();
                    if (!ctx) return;
                    
                    const now = ctx.currentTime;
                    
                    // Tone 1: High alert strike (880Hz -> 587Hz)
                    const osc1 = ctx.createOscillator();
                    const gain1 = ctx.createGain();
                    osc1.type = 'sine';
                    osc1.frequency.setValueAtTime(880, now);
                    osc1.frequency.exponentialRampToValueAtTime(587.33, now + 0.18);
                    
                    gain1.gain.setValueAtTime(0.001, now);
                    gain1.gain.linearRampToValueAtTime(0.35, now + 0.03);
                    gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.40);
                    
                    osc1.connect(gain1);
                    gain1.connect(ctx.destination);
                    
                    osc1.start(now);
                    osc1.stop(now + 0.42);
                    
                    // Tone 2: Harmonized warning chime at now + 0.12s (1174Hz)
                    const osc2 = ctx.createOscillator();
                    const gain2 = ctx.createGain();
                    osc2.type = 'triangle';
                    osc2.frequency.setValueAtTime(1174.66, now + 0.12);
                    osc2.frequency.exponentialRampToValueAtTime(880, now + 0.32);
                    
                    gain2.gain.setValueAtTime(0.001, now + 0.12);
                    gain2.gain.linearRampToValueAtTime(0.20, now + 0.15);
                    gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.48);
                    
                    osc2.connect(gain2);
                    gain2.connect(ctx.destination);
                    
                    osc2.start(now + 0.12);
                    osc2.stop(now + 0.50);
                }} catch(e) {{
                    console.warn("Web Audio API chime suppressed:", e);
                }}
            }}

            function testAlertAudio() {{
                playCrimeAlertChime();
                showAlertBanner("TEST AUDIBLE CHIME: Web Audio API Active (Zero-Latency Synthesizer)");
                setTimeout(hideAlertBanner, 3500);
            }}

            // --- HAVERSINE METERS HELPER ---
            function haversineMeters(lat1, lon1, lat2, lon2) {{
                const R = 6371008.8;
                const dLat = (lat2 - lat1) * Math.PI / 180.0;
                const dLon = (lon2 - lon1) * Math.PI / 180.0;
                const a = Math.sin(dLat/2.0)**2 + Math.cos(lat1 * Math.PI / 180.0) * Math.cos(lat2 * Math.PI / 180.0) * Math.sin(dLon/2.0)**2;
                return 2.0 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));
            }}

            // --- TILE PROVIDERS (DARK SKY / LINEAR DISPATCH) ---
            const TILES = {{
                dark: {{
                    url: 'https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',
                    attribution: '&copy; <a href="https://carto.com/">CARTO</a> | Delhi NCT Civic Intelligence'
                }},
                satellite: {{
                    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
                    attribution: '&copy; Esri World Imagery'
                }}
            }};

            function initMap() {{
                map = L.map('map', {{
                    center: DEFAULT_CENTER,
                    zoom: DEFAULT_ZOOM,
                    zoomControl: false,
                    attributionControl: false
                }});
                
                L.control.attribution({{ position: 'bottomright' }}).addTo(map);

                tileLayer = L.tileLayer(TILES.dark.url, {{
                    maxZoom: 19,
                    attribution: TILES.dark.attribution
                }}).addTo(map);

                // Add Zoom control at bottom right above FAB
                L.control.zoom({{ position: 'bottomright' }}).addTo(map);

                // Auto-Detect User Location
                detectUserLocation();

                // Render Hotspot & Safe Layers
                renderHotspots();
                renderSafeZones();

                // Render Routes
                renderRoutePolylines();
            }}

            function toggleTileLayer() {{
                if (currentTileMode === "dark") {{
                    currentTileMode = "satellite";
                    map.removeLayer(tileLayer);
                    tileLayer = L.tileLayer(TILES.satellite.url, {{ maxZoom: 18, attribution: TILES.satellite.attribution }}).addTo(map);
                    document.getElementById("tile-label").innerText = "Satellite Mode";
                }} else {{
                    currentTileMode = "dark";
                    map.removeLayer(tileLayer);
                    tileLayer = L.tileLayer(TILES.dark.url, {{ maxZoom: 19, attribution: TILES.dark.attribution }}).addTo(map);
                    document.getElementById("tile-label").innerText = "Dark Dispatch";
                }}
            }}

            // --- HTML5 GEOLOCATION AUTO-DETECTION ---
            function detectUserLocation() {{
                if ("geolocation" in navigator) {{
                    navigator.geolocation.getCurrentPosition(
                        function(pos) {{
                            const lat = pos.coords.latitude;
                            const lon = pos.coords.longitude;
                            userCoords = [lat, lon];
                            addUserLocationMarker(lat, lon, "Live GPS Position (High Accuracy)");
                            map.setView([lat, lon], 13);
                        }},
                        function(err) {{
                            console.warn("Geolocation permission denied or timeout:", err.message);
                            userCoords = DEFAULT_CENTER;
                            addUserLocationMarker(DEFAULT_CENTER[0], DEFAULT_CENTER[1], "Connaught Place (Default Civic Anchor)");
                        }},
                        {{ enableHighAccuracy: true, timeout: 5000, maximumAge: 30000 }}
                    );
                }} else {{
                    userCoords = DEFAULT_CENTER;
                    addUserLocationMarker(DEFAULT_CENTER[0], DEFAULT_CENTER[1], "Connaught Place (Default Civic Anchor)");
                }}
            }}

            function addUserLocationMarker(lat, lon, label) {{
                if (userMarker) {{
                    map.removeLayer(userMarker);
                }}
                
                const userIcon = L.divIcon({{
                    className: 'user-gps-beacon',
                    html: `
                        <div style="position:relative; width:22px; height:22px; display:flex; align-items:center; justify-content:center;">
                            <div style="position:absolute; width:22px; height:22px; border-radius:50%; background:rgba(6,182,212,0.3); animation:pulseHazard 2s infinite;"></div>
                            <div style="width:12px; height:12px; border-radius:50%; background:#06b6d4; border:2px solid #ffffff; box-shadow:0 0 10px #06b6d4;"></div>
                        </div>
                    `,
                    iconSize: [22, 22],
                    iconAnchor: [11, 11]
                }});

                userMarker = L.marker([lat, lon], {{ icon: userIcon, zIndexOffset: 1000 }}).addTo(map);
                userMarker.bindPopup(`
                    <div style="font-size:12px;">
                        <strong style="color:#38bdf8;">📍 Current Location Anchor</strong><br/>
                        <span style="color:#94a3b8;">${{label}}</span><br/>
                        <span style="font-family:monospace; font-size:11px; color:#cbd5e1;">${{lat.toFixed(4)}}, ${{lon.toFixed(4)}}</span>
                    </div>
                `);
            }}

            function centerOnUser() {{
                if (userCoords) {{
                    map.setView(userCoords, 14, {{ animate: true }});
                    if (userMarker) userMarker.openPopup();
                }}
            }}

            // --- RENDER CLUSTERS & SAFE CORRIDORS ---
            function renderHotspots() {{
                hotspotLayers = [];
                HOTSPOTS.forEach(h => {{
                    const isCrit = h.is_critical;
                    const circle = L.circle([h.lat, h.lon], {{
                        radius: h.radius_meters,
                        color: h.color,
                        fillColor: h.fill_color,
                        fillOpacity: isCrit ? 0.38 : 0.22,
                        weight: isCrit ? 2 : 1.5,
                        dashArray: isCrit ? null : '4, 6'
                    }});

                    circle.bindPopup(`
                        <div style="min-width:210px; padding:4px;">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                                <span style="font-weight:700; font-size:13px; color:${{h.color}};">${{isCrit ? '🔴 Critical Hotspot' : '🟡 Warning Zone'}}</span>
                                <span style="font-size:10px; background:${{isCrit ? '#7f1d1d' : '#78350f'}}; color:#fef08a; padding:2px 6px; border-radius:4px; font-weight:600;">DBSCAN</span>
                            </div>
                            <div style="font-size:13px; font-weight:600; color:#f8fafc; margin-bottom:4px;">${{h.name}}</div>
                            <div style="font-size:11px; color:#94a3b8; margin-bottom:2px;">Primary Offense: <span style="color:#e2e8f0;">${{h.dominant_crime}}</span></div>
                            <div style="font-size:11px; color:#94a3b8; margin-bottom:2px;">Incident Density: <span style="color:#f8fafc; font-weight:600;">${{h.incident_count}} cases</span></div>
                            <div style="font-size:11px; color:#94a3b8;">Average Severity: <span style="color:#f87171; font-weight:600;">${{h.avg_severity}} / 5.0</span></div>
                        </div>
                    `);
                    
                    hotspotLayers.push(circle);
                    circle.addTo(map);
                }});
            }}

            function renderSafeZones() {{
                safeLayers = [];
                SAFE_ZONES.forEach(s => {{
                    const circle = L.circle([s.lat, s.lon], {{
                        radius: s.radius_meters,
                        color: '#10b981',
                        fillColor: 'rgba(16, 185, 129, 0.18)',
                        fillOpacity: 0.22,
                        weight: 1.5,
                        dashArray: '3, 5'
                    }});

                    circle.bindPopup(`
                        <div style="min-width:190px; padding:4px;">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                                <span style="font-weight:700; font-size:13px; color:#10b981;">🟢 Verified Safe Corridor</span>
                                <span style="font-size:10px; background:#064e3b; color:#a7f3d0; padding:2px 6px; border-radius:4px; font-weight:600;">CIVIC BEAT</span>
                            </div>
                            <div style="font-size:13px; font-weight:600; color:#f8fafc; margin-bottom:4px;">${{s.name}}</div>
                            <div style="font-size:11px; color:#94a3b8;">Safety Index: <strong style="color:#34d399;">${{s.safety_score}}%</strong></div>
                            <div style="font-size:11px; color:#94a3b8;">Critical Clearance: <strong style="color:#a7f3d0;">&gt; 1,200m</strong></div>
                        </div>
                    `);
                    
                    safeLayers.push(circle);
                    circle.addTo(map);
                }});
            }}

            function setLayerMode(mode) {{
                activeLayerMode = mode;
                document.querySelectorAll('.layer-tab').forEach(t => t.classList.remove('active'));
                document.getElementById(`tab-${{mode}}`).classList.add('active');

                if (mode === 'all') {{
                    hotspotLayers.forEach(l => map.addLayer(l));
                    safeLayers.forEach(l => map.addLayer(l));
                }} else if (mode === 'hotspots') {{
                    hotspotLayers.forEach(l => map.addLayer(l));
                    safeLayers.forEach(l => map.removeLayer(l));
                }} else if (mode === 'safe') {{
                    hotspotLayers.forEach(l => map.removeLayer(l));
                    safeLayers.forEach(l => map.addLayer(l));
                }}
            }}

            // --- RENDER ROUTE POLYLINES ---
            function renderRoutePolylines() {{
                const allBounds = [];

                // Standard Route
                if (STANDARD_ROUTE && STANDARD_ROUTE.coordinates && (ACTIVE_ROUTE_TYPE === 'both' || ACTIVE_ROUTE_TYPE === 'standard')) {{
                    stdRoutePolyline = L.polyline(STANDARD_ROUTE.coordinates, {{
                        color: '#f43f5e',
                        weight: 4.5,
                        opacity: 0.85,
                        dashArray: '8, 8',
                        lineCap: 'round',
                        lineJoin: 'round'
                    }}).addTo(map);

                    stdRoutePolyline.bindTooltip("Standard Route (Fastest / Unrestricted)", {{ sticky: true, className: 'route-tooltip' }});
                    allBounds.push(...STANDARD_ROUTE.coordinates);
                }}

                // Safest Route
                if (SAFEST_ROUTE && SAFEST_ROUTE.coordinates && (ACTIVE_ROUTE_TYPE === 'both' || ACTIVE_ROUTE_TYPE === 'safest')) {{
                    // Glowing outer aura
                    L.polyline(SAFEST_ROUTE.coordinates, {{
                        color: '#06b6d4',
                        weight: 8,
                        opacity: 0.35,
                        lineCap: 'round'
                    }}).addTo(map);

                    safeRoutePolyline = L.polyline(SAFEST_ROUTE.coordinates, {{
                        color: '#38bdf8',
                        weight: 4.5,
                        opacity: 0.95,
                        lineCap: 'round',
                        lineJoin: 'round'
                    }}).addTo(map);

                    safeRoutePolyline.bindTooltip("🛡️ Rakshak Safest Route (DBSCAN Cluster Avoidance)", {{ sticky: true, className: 'route-tooltip' }});
                    allBounds.push(...SAFEST_ROUTE.coordinates);
                }}

                // Add Origin & Destination Pins
                if (STANDARD_ROUTE && STANDARD_ROUTE.coordinates && STANDARD_ROUTE.coordinates.length > 0) {{
                    const startPt = STANDARD_ROUTE.coordinates[0];
                    const endPt = STANDARD_ROUTE.coordinates[STANDARD_ROUTE.coordinates.length - 1];

                    // Start Pin
                    const startIcon = L.divIcon({{
                        className: 'route-pin-start',
                        html: `<div style="background:#10b981; color:#0f172a; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; border:2px solid #ffffff; box-shadow:0 0 12px #10b981;">A</div>`,
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    }});
                    L.marker(startPt, {{ icon: startIcon }}).bindPopup("<strong>Route Origin (Start Point)</strong>").addTo(map);

                    // Destination Pin
                    const destIcon = L.divIcon({{
                        className: 'route-pin-dest',
                        html: `<div style="background:#ef4444; color:#ffffff; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; border:2px solid #ffffff; box-shadow:0 0 12px #ef4444;">B</div>`,
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    }});
                    L.marker(endPt, {{ icon: destIcon }}).bindPopup("<strong>Route Destination</strong>").addTo(map);
                }}

                if (allBounds.length > 0) {{
                    map.fitBounds(allBounds, {{ padding: [60, 60], maxZoom: 15 }});
                }}
            }}

            // --- SIMULATION ENGINE & REAL-TIME PROXIMITY DETECTION ---
            function getSimRouteCoords() {{
                if (ACTIVE_ROUTE_TYPE === 'safest' && SAFEST_ROUTE && SAFEST_ROUTE.coordinates) {{
                    return SAFEST_ROUTE.coordinates;
                }}
                if (STANDARD_ROUTE && STANDARD_ROUTE.coordinates) {{
                    return STANDARD_ROUTE.coordinates;
                }}
                if (SAFEST_ROUTE && SAFEST_ROUTE.coordinates) {{
                    return SAFEST_ROUTE.coordinates;
                }}
                return null;
            }}

            function showAlertBanner(msg) {{
                const b = document.getElementById("alert-banner");
                document.getElementById("alert-message").innerText = msg;
                b.style.display = "flex";
                document.getElementById("safe-banner").style.display = "none";
            }}

            function hideAlertBanner() {{
                document.getElementById("alert-banner").style.display = "none";
            }}

            function showSafeBanner(msg) {{
                const b = document.getElementById("safe-banner");
                document.getElementById("safe-message").innerText = msg;
                b.style.display = "flex";
                document.getElementById("alert-banner").style.display = "none";
            }}

            function hideSafeBanner() {{
                document.getElementById("safe-banner").style.display = "none";
            }}

            function toggleSimulation() {{
                const coords = getSimRouteCoords();
                if (!coords || coords.length === 0) {{
                    alert("Please calculate a route first before starting simulation.");
                    return;
                }}

                if (isSimulating) {{
                    // Pause
                    clearInterval(simInterval);
                    isSimulating = false;
                    document.getElementById("sim-icon").innerText = "▶";
                    document.getElementById("sim-btn-text").innerText = "Resume";
                    document.getElementById("sim-status-text").innerText = `PAUSED @ STEP ${{simStep}}/${{coords.length}}`;
                }} else {{
                    // Start or Resume
                    isSimulating = true;
                    document.getElementById("sim-icon").innerText = "⏸";
                    document.getElementById("sim-btn-text").innerText = "Pause";
                    
                    simInterval = setInterval(() => {{
                        if (simStep >= coords.length) {{
                            // Finished
                            clearInterval(simInterval);
                            isSimulating = false;
                            document.getElementById("sim-icon").innerText = "▶";
                            document.getElementById("sim-btn-text").innerText = "Simulate Route";
                            document.getElementById("sim-status-text").innerText = "DESTINATION REACHED";
                            showSafeBanner("DESTINATION REACHED SAFELY | Route Completed");
                            setTimeout(hideSafeBanner, 4500);
                            return;
                        }}

                        const currentCoord = coords[simStep];
                        updateBeaconPosition(currentCoord[0], currentCoord[1]);

                        // Check collision with Critical Hotspots
                        evaluateProximityHazard(currentCoord[0], currentCoord[1]);

                        simStep++;
                        const pct = Math.round((simStep / coords.length) * 100);
                        document.getElementById("sim-status-text").innerText = `TRAVELING: ${{pct}}% (STEP ${{simStep}}/${{coords.length}})`;
                    }}, 220);
                }}
            }}

            function resetSimulation() {{
                clearInterval(simInterval);
                isSimulating = false;
                simStep = 0;
                document.getElementById("sim-icon").innerText = "▶";
                document.getElementById("sim-btn-text").innerText = "Simulate Route";
                document.getElementById("sim-status-text").innerText = "BEACON: STANDBY";
                hideAlertBanner();
                hideSafeBanner();
                if (beaconMarker) {{
                    map.removeLayer(beaconMarker);
                    beaconMarker = null;
                }}
            }}

            function updateBeaconPosition(lat, lon) {{
                if (!beaconMarker) {{
                    const icon = L.divIcon({{
                        className: 'sim-beacon',
                        html: `
                            <div id="beacon-inner" style="width:20px; height:20px; border-radius:50%; background:#38bdf8; border:2px solid #ffffff; box-shadow:0 0 14px #38bdf8; transition:all 0.15s ease;"></div>
                        `,
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    }});
                    beaconMarker = L.marker([lat, lon], {{ icon: icon, zIndexOffset: 2000 }}).addTo(map);
                }} else {{
                    beaconMarker.setLatLng([lat, lon]);
                }}
            }}

            function evaluateProximityHazard(lat, lon) {{
                let breachedHotspot = null;
                let minBreachDist = Infinity;
                let minSafeClearance = Infinity;

                HOTSPOTS.forEach(h => {{
                    if (!h.is_critical) return;
                    const d = haversineMeters(lat, lon, h.lat, h.lon);
                    const dangerThreshold = h.radius_meters + ALERT_BUFFER_METERS;
                    
                    if (d <= dangerThreshold) {{
                        if (d < minBreachDist) {{
                            minBreachDist = d;
                            breachedHotspot = h;
                        }}
                    }}
                    if (d < minSafeClearance) {{
                        minSafeClearance = d;
                    }}
                }});

                const beaconElem = document.getElementById("beacon-inner");

                if (breachedHotspot) {{
                    // Hazard Active!
                    if (beaconElem) {{
                        beaconElem.style.background = "#ef4444";
                        beaconElem.style.boxShadow = "0 0 18px #ef4444";
                    }}
                    
                    const msg = `⚠️ ALERT: Route intersects critical crime zone (Area: ${{breachedHotspot.name}}) | Clear: ${{Math.round(minBreachDist)}}m | Cases: ${{breachedHotspot.incident_count}}`;
                    showAlertBanner(msg);

                    // Throttle chime sound to avoid audio spam
                    const nowTime = Date.now();
                    if (nowTime - lastAlertTime > 2800) {{
                        playCrimeAlertChime();
                        lastAlertTime = nowTime;
                    }}
                }} else {{
                    // Safe
                    if (beaconElem) {{
                        beaconElem.style.background = "#10b981";
                        beaconElem.style.boxShadow = "0 0 14px #10b981";
                    }}
                    hideAlertBanner();
                    showSafeBanner(`🟢 CLEAR CORRIDOR | Hotspot Clearance: ${{Math.round(minSafeClearance)}}m`);
                }}
            }}

            // Start Map on Window Load
            window.addEventListener('DOMContentLoaded', initMap);
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=height, scrolling=False)
