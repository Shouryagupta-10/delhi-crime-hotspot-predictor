"""
Interactive Folium Geospatial Map Renderer for Delhi Crime & Premises
Renders choropleths, density heatmaps, and DBSCAN hotspot corridor polygons/circles.
"""

import folium
from folium.plugins import HeatMap, MarkerCluster, LocateControl, Fullscreen

DELHI_CENTER = [28.6139, 77.2090]

def create_delhi_crime_map(df_filtered, hotspots_df=None, show_heatmap=True, show_hotspots=True, show_pins=True, user_location=None, show_future_heatmap=False, predictor=None, zoom_level=None):
    """
    Renders an interactive Folium map with OpenStreetMap/CartoDB tiles,
    crime density heatmap, DBSCAN cluster centroids, premises incident pins,
    and GPS user location tracking with dynamic zoom controls.
    """
    # If user location is active, center on user, else default Delhi center
    center_loc = [user_location[0], user_location[1]] if user_location else DELHI_CENTER
    if zoom_level is not None:
        zoom_lvl = int(zoom_level)
    else:
        zoom_lvl = 13 if user_location else 11

    m = folium.Map(
        location=center_loc,
        zoom_start=zoom_lvl,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True,
        zoom_control=True
    )

    # Fullscreen control for immersive zooming
    Fullscreen(
        position="topleft",
        title="Expand to Fullscreen View",
        title_cancel="Exit Fullscreen",
        force_separate_button=True
    ).add_to(m)

    # GPS Browser Locate Control Plugin with continuous tracking
    LocateControl(
        auto_start=False,
        flyTo=True,
        keepCurrentZoomLevel=False,
        strings={
            "title": "📍 Track My Live GPS Movement",
            "popup": "You are within {distance} {unit} from this location"
        },
        locateOptions={"enableHighAccuracy": True, "maxZoom": 16, "watch": True}
    ).add_to(m)

    # 0. User Location Marker (if detected)
    if user_location is not None:
        u_lat, u_lon = user_location[0], user_location[1]
        user_group = folium.FeatureGroup(name="📍 Your Current Location", show=True)
        
        # Outer radar / safety radius
        folium.Circle(
            location=[u_lat, u_lon],
            radius=500,
            color="#2563EB",
            fill=True,
            fill_color="#3B82F6",
            fill_opacity=0.15,
            tooltip="500m Immediate Vicinity"
        ).add_to(user_group)

        # Pin marker
        folium.Marker(
            location=[u_lat, u_lon],
            popup=folium.Popup(
                f"""
                <div style="font-family: sans-serif; font-size: 12px; width: 180px;">
                    <b style="color: #1D4ED8;">📍 Your Current Location</b><br/>
                    <b>Lat:</b> {u_lat:.4f}<br/>
                    <b>Lon:</b> {u_lon:.4f}<br/>
                    <span style="color: #059669; font-size: 11px;">Live GPS Tracking Active</span>
                </div>
                """,
                max_width=200
            ),
            tooltip="📍 You Are Here",
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(user_group)
        user_group.add_to(m)
            # 1.5 Future Predictive Heatmap Layer (AI generated grid for tomorrow)
    if show_future_heatmap and predictor and predictor.is_trained:
        import numpy as np
        from datetime import datetime, timedelta
        
        future_heat_data = []
        # Predict for tomorrow at 22:00 (Night time high-risk window)
        tomorrow = datetime.now() + timedelta(days=1)
        future_day = tomorrow.strftime("%A")
        future_hour = 22 
        
        # Create a spatial grid over Delhi to predict future crimes
        lat_min, lat_max = 28.40, 28.88
        lon_min, lon_max = 76.85, 77.35
        
        for lat_grid in np.arange(lat_min, lat_max, 0.015):
            for lon_grid in np.arange(lon_min, lon_max, 0.015):
                risk_res = predictor.predict_risk("New Delhi", "Street & Public Roadways", future_hour, future_day, lat_grid, lon_grid)
                
                # Only plot points that have a high likelihood of future crime
                if risk_res["high_risk_probability"] > 50.0:
                    future_heat_data.append([lat_grid, lon_grid, risk_res["high_risk_probability"] / 100.0])
        
        if future_heat_data:
            HeatMap(
                future_heat_data,
                radius=25,
                blur=20,
                max_zoom=13,
                min_opacity=0.5,
                gradient={0.4: "#8B5CF6", 0.7: "#D946EF", 1.0: "#EC4899"} # Futuristic Purple/Pink
            ).add_to(folium.FeatureGroup(name="🔮 Future Crime Predictions").add_to(m))
    
    # 1. HeatMap Layer
    if show_heatmap and not df_filtered.empty:
        heat_data = [
            [row["latitude"], row["longitude"], float(row["risk_index"])]
            for _, row in df_filtered.iterrows()
        ]
        HeatMap(
            heat_data,
            radius=15,
            blur=18,
            max_zoom=13,
            min_opacity=0.35,
            gradient={0.2: "#3B82F6", 0.5: "#F59E0B", 0.8: "#EF4444", 1.0: "#7F1D1D"}
        ).add_to(m)
        
    # 2. DBSCAN Hotspot Overlays
    if show_hotspots and hotspots_df is not None and not hotspots_df.empty:
        hotspot_group = folium.FeatureGroup(name="DBSCAN Hotspot Clusters")
        for _, h in hotspots_df.iterrows():
            c_lat = h["centroid_lat"]
            c_lon = h["centroid_lon"]
            cnt = h["incident_count"]
            risk = h["avg_risk"]
            
            # Color and size based on risk & volume
            if risk >= 0.60:
                color = "#DC2626"
                fill_color = "#EF4444"
            elif risk >= 0.45:
                color = "#D97706"
                fill_color = "#F59E0B"
            else:
                color = "#2563EB"
                fill_color = "#60A5FA"
                
            radius = min(45, max(12, int(cnt * 0.25)))
            
            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 12px; width: 230px;">
                <h4 style="margin: 0 0 6px 0; color: {color};">Hotspot #{int(h['cluster_id'])}: {h['district']}</h4>
                <b>Incidents:</b> {cnt}<br/>
                <b>Dominant Premises:</b> {h['dominant_premises']}<br/>
                <b>Primary Crime:</b> {h['primary_crime']}<br/>
                <b>Average Risk Index:</b> {risk:.2f}<br/>
                <hr style="margin: 6px 0; border: 0; border-top: 1px solid #E5E7EB;"/>
                <span style="color: #4B5563; font-size: 11px;">Identified via Haversine DBSCAN (&epsilon;=600m)</span>
            </div>
            """
            
            folium.CircleMarker(
                location=[c_lat, c_lon],
                radius=radius,
                color=color,
                weight=2,
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.45,
                popup=folium.Popup(popup_html, max_width=260)
            ).add_to(hotspot_group)
            
        hotspot_group.add_to(m)
        
    # 3. Incident Pins (Clustered for performance)
    if show_pins and not df_filtered.empty:
        # Sample if > 1500 to maintain smooth 60fps browser rendering
        sample_df = df_filtered.sample(n=min(1200, len(df_filtered)), random_state=42)
        marker_cluster = MarkerCluster(name="Individual Premises Incidents").add_to(m)
        
        for _, row in sample_df.iterrows():
            level = row["risk_level"]
            pin_color = "red" if level == "High" else ("orange" if level == "Medium" else "green")
            
            tooltip = f"[{row['hour']:02d}:00] {row['crime_category']} @ {row['premises_type']}"
            popup_content = f"""
            <div style="font-family: sans-serif; font-size: 11px; width: 210px;">
                <b style="color: #111827;">{row['record_id']}</b><br/>
                <b>District:</b> {row['district']} ({row['police_station']})<br/>
                <b>Premises:</b> {row['landmark_premise']} ({row['premises_type']})<br/>
                <b>Crime:</b> {row['crime_category']}<br/>
                <b>Statute:</b> {row['statutory_ipc']}<br/>
                <b>Time:</b> {row['day_of_week']}, {row['hour']:02d}:{row['minute']:02d}<br/>
                <b>Risk:</b> <span style="font-weight: bold; color: {pin_color};">{row['risk_level']} ({row['risk_index']})</span>
            </div>
            """
            
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color=pin_color,
                fill=True,
                fill_opacity=0.7,
                tooltip=tooltip,
                popup=folium.Popup(popup_content, max_width=250)
            ).add_to(marker_cluster)

    # 4. Verified Safe Havens & Protected Low-Risk Corridors
    safe_zones = [
        {"name": "Chanakyapuri Diplomatic Enclave", "lat": 28.5983, "lon": 77.1912, "desc": "24/7 CCTV & Diplomatic Static Pickets"},
        {"name": "Delhi Cantt Defense Corridor", "lat": 28.5898, "lon": 77.1325, "desc": "Military Police & Regulated Access Zone"},
        {"name": "Civil Lines VIP & Raj Niwas Enclave", "lat": 28.6820, "lon": 77.2180, "desc": "High-Density Patrol & Secure Perimeter"},
        {"name": "India Gate & Kartavya Path", "lat": 28.6129, "lon": 77.2295, "desc": "Central Reserve & Drone Surveillance"},
    ]
    safe_group = folium.FeatureGroup(name="🛡️ Safe Havens & Low-Risk Zones", show=True)
    for s in safe_zones:
        folium.Circle(
            location=[s["lat"], s["lon"]],
            radius=450,
            color="#10B981",
            fill=True,
            fill_color="#34D399",
            fill_opacity=0.25,
            tooltip=f"🛡️ Safe Haven: {s['name']}",
            popup=folium.Popup(f"<div style='font-family: sans-serif; font-size: 12px;'><b>🛡️ {s['name']}</b><br/><span style='color: #059669;'>Verified Safe Corridor (&lt;15% Risk)</span><br/>{s['desc']}</div>", max_width=220)
        ).add_to(safe_group)
    safe_group.add_to(m)

    folium.LayerControl().add_to(m)
    return m


def create_smooth_realtime_leaflet_html(hotspots_df=None, initial_user_lat=None, initial_user_lon=None, initial_zoom=13, incidents_df=None):
    """
    Generates a standalone, silky-smooth 60fps Leaflet HTML/JS component
    matching the Once UI / Magic Portfolio dark glassmorphic design system:
    - Dedicated Top Navbar positioned OUTSIDE and above the map canvas (uncluttered view)
    - Predictive Live Search with instant autocomplete dropdown for Delhi NCT
    - Watermark-free Basemaps: Esri Dark Canvas (default), Esri Satellite, OpenStreetMap
    - Marker Clustering for individual crime incidents (Leaflet.markercluster)
    - Rich Hotspot & Safe Haven popups with real Unsplash Delhi landmark imagery
    - Continuous navigator.geolocation.watchPosition tracking with live radar pulse
    - High-contrast breadcrumbs trail & distance-based threat proximity detection
    - Route simulation & dedicated floating geospatial zoom dock
    """
    import json

    landmark_images = {
        "Rajiv Chowk": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "Connaught Place": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "Kashmere Gate": "https://images.unsplash.com/photo-1597040663342-45b6af3d91a5?w=500&auto=format&fit=crop&q=80",
        "Seelampur": "https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=500&auto=format&fit=crop&q=80",
        "Anand Vihar": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=500&auto=format&fit=crop&q=80",
        "Jahangirpuri": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=500&auto=format&fit=crop&q=80",
        "Chandni Chowk": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=500&auto=format&fit=crop&q=80",
        "Karol Bagh": "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?w=500&auto=format&fit=crop&q=80",
        "Saket": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=500&auto=format&fit=crop&q=80",
        "India Gate": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "Chanakyapuri": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=500&auto=format&fit=crop&q=80",
        "Delhi Cantt": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=500&auto=format&fit=crop&q=80",
        "Civil Lines": "https://images.unsplash.com/photo-1572945753563-3001a331c857?w=500&auto=format&fit=crop&q=80",
        "default": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80"
    }

    hotspot_records = []
    if hotspots_df is not None and not hotspots_df.empty:
        for _, r in hotspots_df.iterrows():
            avg_risk = float(r.get("avg_risk", 0.5))
            d_name = str(r.get('district', 'Delhi'))
            p_name = str(r.get('dominant_premises', 'Hotspot'))
            
            img = landmark_images["default"]
            for k in landmark_images:
                if k.lower() in d_name.lower() or k.lower() in p_name.lower():
                    img = landmark_images[k]
                    break

            hotspot_records.append({
                "id": str(r.get("cluster_id", "")),
                "name": f"{d_name} - {p_name}",
                "district": d_name,
                "lat": float(r.get("centroid_lat", 28.6139)),
                "lon": float(r.get("centroid_lon", 77.2090)),
                "crime": str(r.get("primary_crime", "Street Crime")),
                "premises": p_name,
                "riskScore": avg_risk,
                "riskLevel": "HIGH" if avg_risk >= 0.60 else ("MEDIUM" if avg_risk >= 0.45 else "LOW"),
                "incidents": int(r.get("incident_count", 50)),
                "image": img
            })
    else:
        hotspot_records = [
            {"id": "H1", "name": "Rajiv Chowk Metro & Inner Circle", "district": "New Delhi", "lat": 28.6328, "lon": 77.2197, "crime": "Robbery & Snatching", "premises": "Transit Hub", "riskScore": 0.84, "riskLevel": "HIGH", "incidents": 342, "image": landmark_images["Rajiv Chowk"]},
            {"id": "H2", "name": "Kashmere Gate Terminal", "district": "North", "lat": 28.6675, "lon": 77.2285, "crime": "Luggage Theft & Robbery", "premises": "Interstate Transit", "riskScore": 0.88, "riskLevel": "HIGH", "incidents": 419, "image": landmark_images["Kashmere Gate"]},
            {"id": "H3", "name": "Seelampur Market Corridor", "district": "North-East", "lat": 28.6644, "lon": 77.2711, "crime": "Armed Robbery", "premises": "Commercial Market", "riskScore": 0.91, "riskLevel": "HIGH", "incidents": 488, "image": landmark_images["Seelampur"]},
            {"id": "H4", "name": "Anand Vihar ISBT & Railway", "district": "Shahdara", "lat": 28.6469, "lon": 77.3160, "crime": "Pickpocketing & Burglary", "premises": "Transit Terminal", "riskScore": 0.82, "riskLevel": "HIGH", "incidents": 375, "image": landmark_images["Anand Vihar"]},
            {"id": "H5", "name": "Jahangirpuri Public Corridor", "district": "North-West", "lat": 28.7259, "lon": 77.1685, "crime": "Motor Vehicle Theft", "premises": "Public Roadway", "riskScore": 0.86, "riskLevel": "HIGH", "incidents": 402, "image": landmark_images["Jahangirpuri"]},
            {"id": "H6", "name": "Chandni Chowk Main Bazaar", "district": "Central", "lat": 28.6562, "lon": 77.2301, "crime": "Commercial Burglary", "premises": "Wholesale Market", "riskScore": 0.79, "riskLevel": "HIGH", "incidents": 310, "image": landmark_images["Chandni Chowk"]},
            {"id": "H7", "name": "Karol Bagh Commercial Environs", "district": "Central", "lat": 28.6517, "lon": 77.1906, "crime": "Snatching & Theft", "premises": "Retail Hub", "riskScore": 0.55, "riskLevel": "MEDIUM", "incidents": 172, "image": landmark_images["Karol Bagh"]},
            {"id": "H8", "name": "Saket Mall Corridor", "district": "South", "lat": 28.5284, "lon": 77.2185, "crime": "Vehicle Theft", "premises": "Commercial Mall", "riskScore": 0.52, "riskLevel": "MEDIUM", "incidents": 165, "image": landmark_images["Saket"]},
        ]

    incident_records = []
    if incidents_df is not None and not incidents_df.empty:
        sample_size = min(400, len(incidents_df))
        sample_df = incidents_df.sample(n=sample_size, random_state=42) if len(incidents_df) > sample_size else incidents_df
        for _, r in sample_df.iterrows():
            try:
                incident_records.append({
                    "id": str(r.get("record_id", "")),
                    "lat": float(r.get("latitude", 0)),
                    "lon": float(r.get("longitude", 0)),
                    "crime": str(r.get("crime_category", "Crime")),
                    "premises": str(r.get("premises_type", "Public")),
                    "landmark": str(r.get("landmark_premise", "Delhi")),
                    "riskLevel": str(r.get("risk_level", "Medium")),
                    "riskIndex": float(r.get("risk_index", 0.5)),
                    "hour": int(r.get("hour", 12)),
                    "district": str(r.get("district", "Delhi"))
                })
            except Exception:
                continue

    hotspots_json = json.dumps(hotspot_records)
    incidents_json = json.dumps(incident_records)
    init_lat = initial_user_lat if initial_user_lat else 28.6328
    init_lon = initial_user_lon if initial_user_lon else 77.2197
    init_zoom = int(initial_zoom) if initial_zoom else 13

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Rakshak.ai Clean Sentinel Map</title>
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
      <style>
        * {{ box-sizing: border-box; }}
        html, body {{ 
          margin: 0; 
          padding: 0; 
          height: 100%; 
          width: 100%; 
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Geist", sans-serif; 
          background: #080c14; 
          color: #f8fafc; 
          overflow: hidden; 
        }}
        
        /* Master Layout Container */
        .map-app-container {{
          display: flex;
          flex-direction: column;
          height: 100%;
          width: 100%;
          padding: 8px 10px;
          gap: 8px;
        }}
        
        /* Top Navigation Bar: POSITIONED CLEANLY OUTSIDE THE MAP */
        .map-navbar {{
          flex-shrink: 0;
          background: rgba(14, 18, 26, 0.96);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 14px;
          padding: 8px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
          position: relative;
          z-index: 10000;
        }}
        
        .nav-section {{
          display: flex;
          align-items: center;
          gap: 6px;
        }}
        
        .nav-section-title {{
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          margin-right: 2px;
        }}
        
        /* Predictive Search Box & Autocomplete Dropdown */
        .search-container {{
          position: relative;
          flex: 1;
          min-width: 240px;
          max-width: 380px;
        }}
        
        .search-box {{
          display: flex;
          align-items: center;
          background: rgba(15, 23, 42, 0.85);
          border: 1px solid rgba(255, 255, 255, 0.16);
          border-radius: 9999px;
          padding: 4px 6px 4px 12px;
          gap: 6px;
          transition: all 0.2s ease;
        }}
        .search-box:focus-within {{
          border-color: #38bdf8;
          box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
          background: rgba(15, 23, 42, 0.95);
        }}
        
        .search-lens {{
          font-size: 13px;
          color: #94a3b8;
        }}
        
        .search-input {{
          background: transparent;
          border: none;
          outline: none;
          color: #f8fafc;
          font-size: 12px;
          font-family: inherit;
          width: 100%;
        }}
        .search-input::placeholder {{
          color: #64748b;
        }}
        
        .search-clear-btn {{
          background: none;
          border: none;
          color: #94a3b8;
          font-size: 12px;
          cursor: pointer;
          padding: 2px 6px;
        }}
        .search-clear-btn:hover {{
          color: #fff;
        }}
        
        .btn-go {{
          background: linear-gradient(135deg, #0284c7, #0d9488);
          border: 1px solid #38bdf8;
          color: #fff;
          border-radius: 9999px;
          padding: 4px 12px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.15s;
        }}
        .btn-go:hover {{
          filter: brightness(1.15);
          transform: scale(1.02);
        }}
        
        /* Floating Autocomplete Dropdown */
        .predictive-dropdown {{
          position: absolute;
          top: calc(100% + 6px);
          left: 0;
          right: 0;
          background: rgba(11, 15, 25, 0.97);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 12px;
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.2);
          overflow: hidden;
          z-index: 99999;
          max-height: 280px;
          overflow-y: auto;
        }}
        
        .dropdown-header {{
          font-size: 9.5px;
          font-weight: 800;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          padding: 8px 12px 4px 12px;
          background: rgba(255, 255, 255, 0.02);
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        
        .dropdown-item {{
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 12px;
          cursor: pointer;
          transition: background 0.15s;
          border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }}
        .dropdown-item:last-child {{
          border-bottom: none;
        }}
        .dropdown-item:hover, .dropdown-item.active-item {{
          background: rgba(56, 189, 248, 0.12);
        }}
        
        .dropdown-icon {{
          font-size: 15px;
          flex-shrink: 0;
        }}
        
        .dropdown-info {{
          flex: 1;
          min-width: 0;
        }}
        .dropdown-title {{
          font-size: 12px;
          font-weight: 700;
          color: #f1f5f9;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }}
        .dropdown-subtitle {{
          font-size: 10px;
          color: #94a3b8;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-top: 1px;
        }}
        
        .dropdown-badge {{
          font-size: 9px;
          font-weight: 800;
          padding: 2px 6px;
          border-radius: 9999px;
          text-transform: uppercase;
          flex-shrink: 0;
        }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5); }}
        .badge-safe {{ background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.5); }}
        .badge-transit {{ background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }}
        
        /* Pills & Action Buttons */
        .pill-group {{
          display: flex;
          align-items: center;
          gap: 4px;
        }}
        
        .pill-btn {{
          background: rgba(255, 255, 255, 0.05);
          color: #cbd5e1;
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 9999px;
          padding: 5px 11px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.15s ease;
          user-select: none;
          display: inline-flex;
          align-items: center;
          gap: 4px;
        }}
        .pill-btn:hover {{
          background: rgba(255, 255, 255, 0.12);
          color: #fff;
          border-color: rgba(255, 255, 255, 0.25);
        }}
        .pill-btn.active {{
          background: #0284c7 !important;
          border-color: #38bdf8 !important;
          color: #fff !important;
          box-shadow: 0 0 14px rgba(56, 189, 248, 0.45) !important;
        }}
        
        .action-btn {{
          background: rgba(255, 255, 255, 0.05);
          color: #e2e8f0;
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 9999px;
          padding: 5px 12px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.15s ease;
          display: inline-flex;
          align-items: center;
          gap: 4px;
        }}
        .action-btn:hover {{
          background: rgba(255, 255, 255, 0.12);
          color: #fff;
        }}
        .action-btn.sim-btn {{
          background: rgba(217, 119, 6, 0.2);
          border-color: rgba(245, 158, 11, 0.5);
          color: #fde68a;
        }}
        .action-btn.sim-btn:hover {{
          background: #d97706;
          color: #fff;
        }}
        .action-btn.sim-btn.active {{
          background: #d97706;
          color: #fff;
          box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
        }}
        
        /* Clean Map Viewport Wrapper */
        .map-viewport {{
          flex: 1;
          position: relative;
          border-radius: 14px;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.1);
          min-height: 0;
          background: #080c14;
        }}
        #map {{ 
          height: 100%; 
          width: 100%; 
          background: #080c14; 
        }}
        
        /* Floating Status Pill inside Map (Minimalist, Top Left) */
        .floating-status-pill {{
          position: absolute;
          top: 12px;
          left: 12px;
          z-index: 1000;
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(13, 17, 26, 0.88);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 9999px;
          padding: 5px 12px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
          pointer-events: none;
        }}
        
        .threat-tag {{
          font-weight: 800;
          padding: 2px 8px;
          border-radius: 9999px;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }}
        .tag-high {{ background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.6); }}
        .tag-med {{ background: rgba(245, 158, 11, 0.25); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.6); }}
        .tag-safe {{ background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.6); }}
        
        .status-subtext {{
          font-size: 11px;
          color: #cbd5e1;
          font-weight: 600;
        }}
        
        /* Floating Zoom Dock (Right Edge) */
        .floating-zoom-dock {{
          position: absolute;
          top: 12px;
          right: 12px;
          z-index: 1000;
          display: flex;
          flex-direction: column;
          gap: 4px;
          background: rgba(13, 17, 26, 0.92);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 12px;
          padding: 5px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }}
        .zoom-btn {{
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.05);
          color: #f8fafc;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 7px;
          font-size: 14px;
          font-weight: 800;
          cursor: pointer;
          transition: all 0.15s ease-in-out;
        }}
        .zoom-btn:hover {{
          background: #0284c7;
          border-color: #38bdf8;
          color: #fff;
          transform: scale(1.08);
        }}
        .zoom-indicator {{
          font-size: 9px;
          font-weight: 800;
          text-align: center;
          color: #38bdf8;
          padding: 2px 0;
          font-family: monospace;
          user-select: none;
        }}
        
        /* Bottom Telemetry Bar inside Map */
        .bottom-telemetry {{
          position: absolute;
          bottom: 10px;
          left: 12px;
          right: 12px;
          z-index: 1000;
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
          background: rgba(13, 17, 26, 0.88);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          padding: 6px 14px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.5);
          font-size: 11px;
        }}
        
        .telemetry-readouts {{
          display: flex;
          align-items: center;
          gap: 14px;
        }}
        .tel-item {{
          display: flex;
          flex-direction: column;
        }}
        .tel-label {{
          font-size: 9px;
          font-weight: 800;
          color: #64748b;
          letter-spacing: 0.04em;
        }}
        .val-cyan {{ font-family: monospace; color: #38bdf8; }}
        .val-purple {{ font-family: monospace; color: #a78bfa; }}
        .val-green {{ font-family: monospace; color: #4ade80; }}
        
        .telemetry-legend {{
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 10.5px;
          font-weight: 600;
        }}
        .legend-dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
          margin-right: 3px;
        }}
        .dot-red {{ background: #ef4444; box-shadow: 0 0 6px #ef4444; }}
        .dot-amber {{ background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }}
        .dot-green {{ background: #10b981; box-shadow: 0 0 6px #10b981; }}
        
        /* Pulse Marker */
        .radar-pulse-marker {{
          animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
          0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.8); }}
          70% {{ transform: scale(1.18); box-shadow: 0 0 0 20px rgba(6, 182, 212, 0); }}
          100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }}
        }}
        
        /* Once UI Popups */
        .leaflet-popup-content-wrapper {{ 
          background: #0b0f19 !important; 
          color: #f8fafc !important; 
          border: 1px solid rgba(255, 255, 255, 0.15) !important; 
          border-radius: 14px !important; 
          padding: 0 !important;
          overflow: hidden !important;
          box-shadow: 0 16px 36px rgba(0,0,0,0.7) !important;
        }}
        .leaflet-popup-content {{ margin: 0 !important; line-height: 1.4 !important; }}
        .leaflet-popup-tip {{ background: #0b0f19 !important; }}
        .leaflet-container a.leaflet-popup-close-button {{
          color: #ffffff !important;
          top: 8px !important;
          right: 8px !important;
          background: rgba(0,0,0,0.6) !important;
          border-radius: 50% !important;
          width: 22px !important;
          height: 22px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          border: 1px solid rgba(255,255,255,0.2) !important;
        }}
        
        .cluster-pill {{
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          font-family: monospace;
          font-weight: 800;
          color: #ffffff;
          border: 2px solid #ffffff;
        }}
        
        /* Real-Time Street Navigation HUD */
        .nav-hud {{
          position: absolute;
          top: 10px;
          left: 12px;
          right: 12px;
          max-width: 660px;
          margin: 0 auto;
          z-index: 1100;
          background: rgba(11, 15, 25, 0.94);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(56, 189, 248, 0.45);
          border-radius: 14px;
          box-shadow: 0 14px 36px rgba(0, 0, 0, 0.75), 0 0 24px rgba(56, 189, 248, 0.18);
          overflow: hidden;
          animation: navSlideDown 0.25s ease-out;
        }}
        @keyframes navSlideDown {{
          from {{ transform: translateY(-20px); opacity: 0; }}
          to {{ transform: translateY(0); opacity: 1; }}
        }}
        .nav-hud-main {{
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 9px 14px;
        }}
        .nav-maneuver-icon {{
          width: 42px;
          height: 42px;
          border-radius: 10px;
          background: linear-gradient(135deg, #0284c7, #2563eb);
          border: 1.5px solid #38bdf8;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          font-weight: 900;
          flex-shrink: 0;
          box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
        }}
        .nav-hud-text {{
          flex: 1;
          min-width: 0;
        }}
        .nav-instruction {{
          font-size: 13px;
          font-weight: 800;
          color: #f8fafc;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          line-height: 1.2;
        }}
        .nav-next-street {{
          font-size: 11px;
          color: #94a3b8;
          margin-top: 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }}
        .nav-hud-stats {{
          display: flex;
          align-items: center;
          gap: 12px;
          border-left: 1px solid rgba(255, 255, 255, 0.1);
          border-right: 1px solid rgba(255, 255, 255, 0.1);
          padding: 0 12px;
          flex-shrink: 0;
        }}
        .nav-stat-block {{
          display: flex;
          flex-direction: column;
          align-items: center;
        }}
        .nav-stat-val {{
          font-family: monospace;
          font-size: 13px;
          font-weight: 800;
        }}
        .nav-stat-lbl {{
          font-size: 8px;
          font-weight: 800;
          color: #64748b;
          letter-spacing: 0.05em;
        }}
        .nav-hud-controls {{
          display: flex;
          align-items: center;
          gap: 6px;
          flex-shrink: 0;
        }}
        .nav-action-btn {{
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(255, 255, 255, 0.15);
          color: #e2e8f0;
          font-size: 11px;
          font-weight: 700;
          padding: 6px 9px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.15s ease;
        }}
        .nav-action-btn:hover {{
          background: rgba(255, 255, 255, 0.12);
          color: #fff;
        }}
        .nav-action-btn.btn-play {{
          background: #0284c7;
          border-color: #38bdf8;
          color: #fff;
        }}
        .nav-action-btn.btn-play.active {{
          background: #d97706;
          border-color: #f59e0b;
        }}
        .nav-action-btn.btn-close {{
          background: rgba(239, 68, 68, 0.15);
          border-color: rgba(239, 68, 68, 0.4);
          color: #ef4444;
        }}
        .nav-action-btn.btn-close:hover {{
          background: #dc2626;
          color: #fff;
        }}
        
        /* Steps Drawer */
        .nav-steps-drawer {{
          max-height: 220px;
          overflow-y: auto;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(8, 11, 19, 0.96);
          padding: 8px 12px;
        }}
        .nav-steps-header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 11px;
          font-weight: 700;
          color: #cbd5e1;
          margin-bottom: 6px;
          padding-bottom: 4px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .nav-step-item {{
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 8px;
          border-radius: 6px;
          font-size: 11.5px;
          cursor: pointer;
          transition: background 0.1s ease;
        }}
        .nav-step-item:hover {{
          background: rgba(255, 255, 255, 0.06);
        }}
        .nav-step-item.active {{
          background: rgba(2, 132, 199, 0.25);
          border: 1px solid rgba(56, 189, 248, 0.35);
        }}
        .nav-step-icon {{
          font-size: 14px;
          width: 22px;
          text-align: center;
          flex-shrink: 0;
        }}
        .nav-step-desc {{
          flex: 1;
          color: #e2e8f0;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }}
        .nav-step-dist {{
          font-family: monospace;
          font-size: 11px;
          color: #38bdf8;
          flex-shrink: 0;
        }}
        
        /* Quick Route Modal */
        .quick-route-modal {{
          position: absolute;
          inset: 0;
          z-index: 1200;
          background: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }}
        .quick-route-card {{
          background: #0f172a;
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 16px;
          padding: 18px;
          max-width: 500px;
          width: 100%;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8);
          max-height: 80vh;
          display: flex;
          flex-direction: column;
        }}
        .quick-route-header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
        }}
        .modal-close-btn {{
          background: none;
          border: none;
          color: #94a3b8;
          font-size: 16px;
          cursor: pointer;
        }}
        .modal-close-btn:hover {{ color: #fff; }}
        .quick-route-grid {{
          overflow-y: auto;
          display: grid;
          grid-template-columns: 1fr;
          gap: 6px;
          margin-top: 8px;
          padding-right: 4px;
        }}
        .quick-route-item {{
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 9px;
          padding: 9px 12px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          transition: all 0.15s ease;
        }}
        .quick-route-item:hover {{
          background: rgba(2, 132, 199, 0.18);
          border-color: #38bdf8;
          transform: translateX(2px);
        }}
      </style>
    </head>
    <body>
      <div class="map-app-container">
        
        <!-- Top Navbar: OUTSIDE the map viewport -->
        <header class="map-navbar">
          
          <!-- Predictive Search Box -->
          <div class="search-container">
            <div class="search-box">
              <span class="search-lens">🔍</span>
              <input 
                id="mapSearchInput" 
                class="search-input" 
                type="text" 
                placeholder="Search Delhi (e.g. Rajiv Chowk, Hauz Khas)..." 
                autocomplete="off" 
              />
              <button id="searchClearBtn" class="search-clear-btn" onclick="clearSearchInput()" style="display:none;">✕</button>
              <button id="searchActionBtn" class="btn-go" onclick="executeSearch()">Search</button>
            </div>
            
            <!-- Autocomplete Suggestions Menu -->
            <div id="predictiveDropdown" class="predictive-dropdown" style="display:none;"></div>
          </div>
          
          <!-- Basemap Toggle Group -->
          <div class="nav-section">
            <span class="nav-section-title">BASEMAP:</span>
            <div class="pill-group">
              <button id="btnLayerDark" class="pill-btn active" onclick="switchBasemap('dark')">🌑 Dark</button>
              <button id="btnLayerSat" class="pill-btn" onclick="switchBasemap('satellite')">🛰️ Satellite</button>
              <button id="btnLayerStreet" class="pill-btn" onclick="switchBasemap('street')">🗺️ Street</button>
            </div>
          </div>
          
          <!-- Layer Filters -->
          <div class="nav-section">
            <span class="nav-section-title">LAYERS:</span>
            <div class="pill-group">
              <button id="btnAll" class="pill-btn active" onclick="setLayerFilter('ALL')">All</button>
              <button id="btnHigh" class="pill-btn" onclick="setLayerFilter('HIGH')">🔴 High Risk</button>
              <button id="btnSafe" class="pill-btn" onclick="setLayerFilter('SAFE')">🟢 Safe Havens</button>
              <button id="btnClusterToggle" class="pill-btn active" onclick="toggleIncidentClusters()">📌 Pins</button>
            </div>
          </div>
          
          <!-- Action Controls -->
          <div class="nav-section">
            <button id="btnQuickNav" class="action-btn" style="background: linear-gradient(135deg, #0284c7, #4f46e5); border-color: #38bdf8; font-weight: 700;" onclick="openQuickRouteModal()">🧭 Route / ETA</button>
            <button id="btnSim" class="action-btn sim-btn" onclick="toggleSimulation()">🚀 Sim GPS</button>
            <button class="action-btn" onclick="centerOnMe()">📍 Me</button>
          </div>
          
        </header>
        
        <!-- Clean Map Canvas Viewport -->
        <main class="map-viewport">
          <div id="map"></div>
          
          <!-- Real-Time Street Navigation HUD -->
          <div id="navHud" class="nav-hud" style="display:none;">
            <div class="nav-hud-main">
              <div id="navManeuverIcon" class="nav-maneuver-icon">⬆</div>
              <div class="nav-hud-text">
                <div id="navInstruction" class="nav-instruction">Proceed along route</div>
                <div id="navNextStreet" class="nav-next-street">Calculating street trajectory...</div>
              </div>
              <div class="nav-hud-stats">
                <div class="nav-stat-block">
                  <div id="navEtaText" class="nav-stat-val val-green">-- min</div>
                  <div class="nav-stat-lbl">ETA (LIVE)</div>
                </div>
                <div class="nav-stat-block">
                  <div id="navDistText" class="nav-stat-val val-cyan">-- km</div>
                  <div class="nav-stat-lbl">DISTANCE</div>
                </div>
              </div>
              <div class="nav-hud-controls">
                <button id="navSimPlayBtn" class="nav-action-btn btn-play" onclick="toggleNavDriveSim()" title="Drive route at 60fps">🚀 Drive</button>
                <button class="nav-action-btn" onclick="toggleNavStepsDrawer()" title="View Turn-by-Turn Steps">📋 Turns</button>
                <button class="nav-action-btn btn-close" onclick="clearNavigationRoute(true)" title="Exit Navigation">✕</button>
              </div>
            </div>
            
            <!-- Turn-by-Turn Steps Drawer -->
            <div id="navStepsDrawer" class="nav-steps-drawer" style="display:none;">
              <div class="nav-steps-header">
                <span>🛣️ Real-Time Street Directions (OpenStreetMap / OSRM)</span>
                <span id="navDrawerSummary" class="val-cyan"></span>
              </div>
              <div id="navStepsList" class="nav-steps-list"></div>
            </div>
          </div>

          <!-- Quick Route Destination Selector Modal -->
          <div id="quickRouteModal" class="quick-route-modal" style="display:none;">
            <div class="quick-route-card">
              <div class="quick-route-header">
                <span style="font-size: 13.5px; font-weight: 800; color: #fff; display:flex; align-items:center; gap:6px;">
                  🧭 Choose Navigation Destination
                </span>
                <button class="modal-close-btn" onclick="closeQuickRouteModal()">✕</button>
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin: 6px 0 10px 0;">
                Calculates real-time street turn-by-turn directions, road-accurate distance, and live ETA from your GPS position.
              </div>
              <div class="quick-route-grid" id="quickRouteList"></div>
            </div>
          </div>
          
          <!-- Floating Status Capsule -->
          <div class="floating-status-pill">
            <span id="threatBadge" class="threat-tag tag-safe">🛡️ SAFE BUFFER ZONE</span>
            <span id="closestHotspotText" class="status-subtext">Scanning nearby corridors...</span>
          </div>
          
          <!-- Dedicated Floating Zoom Dock -->
          <div class="floating-zoom-dock" title="Geospatial Zoom Controls">
            <button class="zoom-btn" onclick="zoomInMap()" title="Zoom In (+ / scroll up)">➕</button>
            <div id="zoomLevelDock" class="zoom-indicator">{init_zoom}x</div>
            <button class="zoom-btn" onclick="zoomOutMap()" title="Zoom Out (- / scroll down)">➖</button>
            <button class="zoom-btn" style="font-size: 12px;" onclick="resetZoomMap()" title="Reset to Default Zoom">🔄</button>
            <button class="zoom-btn" style="font-size: 12px;" onclick="fitAllHotspots()" title="Fit All Delhi Hotspots in View">🗺️</button>
          </div>
          
          <!-- Bottom Telemetry Bar -->
          <footer class="bottom-telemetry">
            <div class="telemetry-readouts">
              <div class="tel-item">
                <span class="tel-label">GPS COORDS</span>
                <b id="gpsCoordsText" class="val-cyan">{init_lat:.4f}°N, {init_lon:.4f}°E</b>
              </div>
              <div class="tel-item">
                <span class="tel-label">MAP ZOOM</span>
                <b id="gpsZoomText" class="val-purple">{init_zoom}x (District)</b>
              </div>
              <div class="tel-item">
                <span class="tel-label">PRECISION</span>
                <b id="gpsAccText" class="val-green">&plusmn;15m</b>
              </div>
            </div>
            
            <div class="telemetry-legend">
              <span><span class="legend-dot dot-red"></span> High (&ge;60%)</span>
              <span><span class="legend-dot dot-amber"></span> Med (45-60%)</span>
              <span><span class="legend-dot dot-green"></span> Safe (&lt;45%)</span>
            </div>
          </footer>
          
        </main>
      </div>
      
      <script>
        const HOTSPOTS = {hotspots_json};
        const INCIDENTS = {incidents_json};
        const SAFE_ZONES = [
          {{ id: "S1", name: "Chanakyapuri Diplomatic Enclave", district: "New Delhi", lat: 28.5983, lon: 77.1912, desc: "24/7 CCTV & Diplomatic Static Pickets", riskScore: 0.12, image: "{landmark_images['Chanakyapuri']}" }},
          {{ id: "S2", name: "Delhi Cantt Defense Corridor", district: "South-West", lat: 28.5898, lon: 77.1325, desc: "Military Police & Regulated Access Zone", riskScore: 0.15, image: "{landmark_images['Delhi Cantt']}" }},
          {{ id: "S3", name: "Civil Lines VIP & Raj Niwas Enclave", district: "North", lat: 28.6820, lon: 77.2180, desc: "High-Density Patrol & Secure Perimeter", riskScore: 0.18, image: "{landmark_images['Civil Lines']}" }},
          {{ id: "S4", name: "India Gate & Kartavya Path", district: "New Delhi", lat: 28.6129, lon: 77.2295, desc: "Central Reserve & Drone Surveillance", riskScore: 0.20, image: "{landmark_images['India Gate']}" }}
        ];
        
        // Comprehensive Delhi NCT Landmark & Hotspot Index for Instant Predictive Search
        const DELHI_LOCATIONS = [
          {{ name: "Rajiv Chowk Metro Station", district: "Connaught Place, Central Delhi", lat: 28.6328, lon: 77.2197, type: "transit", badge: "High Risk Hotspot", badgeClass: "badge-danger" }},
          {{ name: "Connaught Place (CP Inner Circle)", district: "New Delhi", lat: 28.6315, lon: 77.2167, type: "commercial", badge: "Commercial Hub", badgeClass: "badge-transit" }},
          {{ name: "Kashmere Gate ISBT & Terminal", district: "North Delhi", lat: 28.6675, lon: 77.2285, type: "transit", badge: "Critical Hotspot", badgeClass: "badge-danger" }},
          {{ name: "Seelampur Market Corridor", district: "North-East Delhi", lat: 28.6644, lon: 77.2711, type: "market", badge: "Critical Hotspot", badgeClass: "badge-danger" }},
          {{ name: "Anand Vihar Railway & Bus Terminal", district: "Shahdara / East Delhi", lat: 28.6469, lon: 77.3160, type: "transit", badge: "High Risk Hotspot", badgeClass: "badge-danger" }},
          {{ name: "Chandni Chowk Main Bazaar", district: "Central / Old Delhi", lat: 28.6562, lon: 77.2301, type: "market", badge: "High Density Area", badgeClass: "badge-danger" }},
          {{ name: "Hauz Khas Village & Lake", district: "South Delhi", lat: 28.5535, lon: 77.1945, type: "colony", badge: "Lifestyle Hub", badgeClass: "badge-transit" }},
          {{ name: "Karol Bagh Commercial Environs", district: "Central Delhi", lat: 28.6517, lon: 77.1906, type: "market", badge: "Medium Risk", badgeClass: "badge-transit" }},
          {{ name: "Saket Select Citywalk & Malls", district: "South Delhi", lat: 28.5284, lon: 77.2185, type: "commercial", badge: "Retail Corridor", badgeClass: "badge-transit" }},
          {{ name: "India Gate & Kartavya Path", district: "New Delhi", lat: 28.6129, lon: 77.2295, type: "monument", badge: "Safe Corridor", badgeClass: "badge-safe" }},
          {{ name: "Chanakyapuri Diplomatic Enclave", district: "New Delhi", lat: 28.5983, lon: 77.1912, type: "safe", badge: "Safe Corridor", badgeClass: "badge-safe" }},
          {{ name: "Delhi Cantt Defense Area", district: "South-West Delhi", lat: 28.5898, lon: 77.1325, type: "safe", badge: "Safe Corridor", badgeClass: "badge-safe" }},
          {{ name: "Civil Lines VIP & Raj Niwas", district: "North Delhi", lat: 28.6820, lon: 77.2180, type: "safe", badge: "Safe Corridor", badgeClass: "badge-safe" }},
          {{ name: "Dwarka Sector 10 & 21", district: "South-West Delhi", lat: 28.5815, lon: 77.0583, type: "colony", badge: "Residential Hub", badgeClass: "badge-transit" }},
          {{ name: "Rohini Sector 13 & 14", district: "North-West Delhi", lat: 28.7160, lon: 77.1147, type: "colony", badge: "Residential Hub", badgeClass: "badge-transit" }},
          {{ name: "Jahangirpuri Corridor", district: "North-West Delhi", lat: 28.7259, lon: 77.1685, type: "corridor", badge: "High Risk Corridor", badgeClass: "badge-danger" }},
          {{ name: "Lajpat Nagar Central Market", district: "South-East Delhi", lat: 28.5677, lon: 77.2433, type: "market", badge: "Commercial Market", badgeClass: "badge-transit" }},
          {{ name: "Vasant Kunj Promenade", district: "South Delhi", lat: 28.5412, lon: 77.1558, type: "commercial", badge: "Commercial Corridor", badgeClass: "badge-transit" }},
          {{ name: "Janakpuri District Centre", district: "West Delhi", lat: 28.6289, lon: 77.0788, type: "commercial", badge: "Transit & Market", badgeClass: "badge-transit" }},
          {{ name: "Pitampura TV Tower Environs", district: "North-West Delhi", lat: 28.6989, lon: 77.1407, type: "colony", badge: "Commercial & Residential", badgeClass: "badge-transit" }},
          {{ name: "Nehru Place Commercial Hub", district: "South-East Delhi", lat: 28.5492, lon: 77.2527, type: "commercial", badge: "IT & Commercial", badgeClass: "badge-transit" }},
          {{ name: "Mayur Vihar Phase 1 & 2", district: "East Delhi", lat: 28.6083, lon: 77.2967, type: "colony", badge: "Residential District", badgeClass: "badge-transit" }},
          {{ name: "South Extension Part 1 & 2", district: "South Delhi", lat: 28.5724, lon: 77.2215, type: "market", badge: "Shopping Ring", badgeClass: "badge-transit" }},
          {{ name: "Rajouri Garden Main Market", district: "West Delhi", lat: 28.6477, lon: 77.1219, type: "market", badge: "Shopping District", badgeClass: "badge-transit" }}
        ];
        
        const SIMULATION_ROUTE = [
          {{ lat: 28.5983, lon: 77.1912, label: "Chanakyapuri Safe Haven" }},
          {{ lat: 28.6139, lon: 77.2090, label: "Rashtrapati Bhavan Perimeter" }},
          {{ lat: 28.6250, lon: 77.2150, label: "Parliament Street Junction" }},
          {{ lat: 28.6300, lon: 77.2170, label: "Entering Connaught Place Outer Ring" }},
          {{ lat: 28.6328, lon: 77.2197, label: "Rajiv Chowk Metro High-Risk Centroid" }},
          {{ lat: 28.6420, lon: 77.2220, label: "Minto Road Railway Bridge Corridor" }},
          {{ lat: 28.6500, lon: 77.2260, label: "Approaching Old Delhi / Chandni Chowk" }},
          {{ lat: 28.6600, lon: 77.2280, label: "Lothian Road towards Kashmere Gate" }},
          {{ lat: 28.6675, lon: 77.2285, label: "Kashmere Gate Terminal (Critical Hotspot)" }}
        ];
        
        function calcDistMeters(lat1, lon1, lat2, lon2) {{
          const R = 6371e3;
          const p1 = lat1 * Math.PI / 180;
          const p2 = lat2 * Math.PI / 180;
          const dp = (lat2 - lat1) * Math.PI / 180;
          const dl = (lon2 - lon1) * Math.PI / 180;
          const a = Math.sin(dp/2)*Math.sin(dp/2) + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)*Math.sin(dl/2);
          return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
        }}
        
        // Init Map
        const map = L.map('map', {{
          center: [{init_lat}, {init_lon}],
          zoom: {init_zoom},
          zoomControl: false,
          attributionControl: false,
          preferCanvas: true,
          scrollWheelZoom: true,
          doubleClickZoom: true,
          touchZoom: true
        }});
        
        // Watermark-free Basemap Tile Layers
        const esriDarkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 19,
          maxNativeZoom: 16
        }});
        const esriDarkRef = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 19,
          maxNativeZoom: 16
        }});
        const darkLayerGroup = L.layerGroup([esriDarkBase, esriDarkRef]);
        
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
          maxZoom: 19
        }});
        
        const streetLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 19
        }});
        
        const tileLayers = {{
          dark: darkLayerGroup,
          satellite: satelliteLayer,
          street: streetLayer
        }};
        
        let currentBasemap = 'dark';
        tileLayers[currentBasemap].addTo(map);
        
        window.switchBasemap = function(layerName) {{
          if (currentBasemap === layerName) return;
          map.removeLayer(tileLayers[currentBasemap]);
          tileLayers[layerName].addTo(map);
          tileLayers[layerName].bringToBack();
          currentBasemap = layerName;
          document.getElementById('btnLayerDark').classList.toggle('active', layerName === 'dark');
          document.getElementById('btnLayerSat').classList.toggle('active', layerName === 'satellite');
          document.getElementById('btnLayerStreet').classList.toggle('active', layerName === 'street');
        }};
        
        setTimeout(() => {{ map.invalidateSize(); }}, 200);
        window.addEventListener('resize', () => {{ map.invalidateSize(); }});
        
        // Breadcrumb Trail Polyline
        const trailPolyline = L.polyline([], {{
          color: '#06b6d4',
          weight: 4,
          opacity: 0.85,
          dashArray: '4, 8',
          lineCap: 'round'
        }}).addTo(map);
        
        let trailWaypoints = [];
        let userMarker = null;
        let userAccuracyCircle = null;
        let markersGroup = L.layerGroup().addTo(map);
        let activeFilter = 'ALL';
        let currentUserPos = {{ lat: {init_lat}, lon: {init_lon} }};
        
        // Incident Clustering Group
        const incidentClusterGroup = L.markerClusterGroup({{
          maxClusterRadius: 40,
          spiderfyOnMaxZoom: true,
          showCoverageOnHover: false,
          iconCreateFunction: function(cluster) {{
            const count = cluster.getChildCount();
            let size = count < 15 ? 30 : (count < 40 ? 36 : 42);
            let glow = count < 15 ? 'rgba(56, 189, 248, 0.5)' : (count < 40 ? 'rgba(245, 158, 11, 0.5)' : 'rgba(239, 68, 68, 0.6)');
            let bg = count < 15 ? '#0284c7' : (count < 40 ? '#d97706' : '#dc2626');
            return L.divIcon({{
              html: `<div class="cluster-pill" style="width:${{size}}px; height:${{size}}px; background:${{bg}}; box-shadow: 0 0 14px ${{glow}}; font-size:11px;">${{count}}</div>`,
              className: '',
              iconSize: [size, size],
              iconAnchor: [size/2, size/2]
            }});
          }}
        }});
        
        let showIncidents = true;
        if (INCIDENTS && INCIDENTS.length > 0) {{
          INCIDENTS.forEach(inc => {{
            const isHigh = inc.riskLevel === 'High';
            const isMed = inc.riskLevel === 'Medium';
            const color = isHigh ? '#ef4444' : (isMed ? '#f59e0b' : '#10b981');
            
            const cm = L.circleMarker([inc.lat, inc.lon], {{
              radius: 5,
              color: color,
              weight: 1.5,
              fillColor: color,
              fillOpacity: 0.8
            }});
            
            cm.bindPopup(`
              <div style="width: 230px; font-family: -apple-system, sans-serif;">
                <div style="background: rgba(255,255,255,0.06); padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                  <span style="font-size: 10px; font-weight: 800; color: ${{color}}; text-transform: uppercase;">${{inc.riskLevel}} Risk Incident</span>
                  <div style="font-weight: 700; color: #fff; font-size: 12px; margin-top: 2px;">${{inc.crime}}</div>
                </div>
                <div style="padding: 10px 12px; font-size: 11px;">
                  <div style="color: #cbd5e1; margin-bottom: 3px;"><b>Premises:</b> ${{inc.premises}}</div>
                  <div style="color: #cbd5e1; margin-bottom: 3px;"><b>Landmark:</b> ${{inc.landmark || 'Delhi NCT'}}</div>
                  <div style="color: #94a3b8; font-size: 10.5px; margin-top: 6px;">${{String(inc.hour).padStart(2, '0')}}:00 hrs &bull; ${{inc.district}} Jurisdiction</div>
                </div>
              </div>
            `);
            incidentClusterGroup.addLayer(cm);
          }});
          map.addLayer(incidentClusterGroup);
        }}
        
        window.toggleIncidentClusters = function() {{
          showIncidents = !showIncidents;
          const btn = document.getElementById('btnClusterToggle');
          if (showIncidents) {{
            map.addLayer(incidentClusterGroup);
            btn.classList.add('active');
          }} else {{
            map.removeLayer(incidentClusterGroup);
            btn.classList.remove('active');
          }}
        }};
        
        function renderZones(filter) {{
          markersGroup.clearLayers();
          
          HOTSPOTS.forEach(h => {{
            if (filter === 'SAFE') return;
            if (filter === 'HIGH' && h.riskLevel !== 'HIGH') return;
            
            const isHigh = h.riskLevel === 'HIGH';
            const color = isHigh ? '#ef4444' : '#f59e0b';
            const radius = isHigh ? 380 : 250;
            
            L.circle([h.lat, h.lon], {{
              radius: radius,
              color: color,
              weight: 1.5,
              fillColor: color,
              fillOpacity: isHigh ? 0.22 : 0.14,
              dashArray: isHigh ? undefined : '5, 5'
            }}).addTo(markersGroup);
            
            const pinHtml = `
              <div style="display:flex; flex-direction:column; align-items:center; cursor:pointer;">
                <div style="width:28px; height:28px; border-radius:50%; background:${{isHigh ? '#dc2626' : '#d97706'}}; box-shadow:0 0 12px ${{color}}; display:flex; align-items:center; justify-content:center; font-size:13px; color:#fff; border: 2px solid #fff;">
                  ${{isHigh ? '🚨' : '⚠️'}}
                </div>
                <div style="font-size:9.5px; font-weight:800; background:#0b0f19; color:${{color}}; border:1px solid ${{color}}; padding:1px 6px; border-radius:4px; margin-top:2px; white-space:nowrap; box-shadow: 0 2px 8px rgba(0,0,0,0.5);">
                  ${{h.name.split(' ')[0]}} (${{Math.round(h.riskScore*100)}}%)
                </div>
              </div>
            `;
            const icon = L.divIcon({{ html: pinHtml, className: '', iconSize: [42, 42], iconAnchor: [21, 21] }});
            const m = L.marker([h.lat, h.lon], {{ icon: icon }}).addTo(markersGroup);
            
            m.bindPopup(`
              <div style="width: 250px; font-family: -apple-system, sans-serif;">
                <div style="position: relative; height: 115px; width: 100%; overflow: hidden; background: #1e293b;">
                  <img src="${{h.image}}" alt="${{h.name}}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'" />
                  <div style="position: absolute; top: 8px; left: 8px; background: ${{color}}; color: #fff; font-size: 9.5px; font-weight: 800; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase;">
                    ${{h.riskLevel}} RISK (${{Math.round(h.riskScore*100)}}%)
                  </div>
                  <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 35px; background: linear-gradient(to top, #0b0f19, transparent);"></div>
                </div>
                <div style="padding: 10px 12px;">
                  <div style="font-size: 13px; font-weight: 800; color: #f8fafc; margin-bottom: 3px; line-height: 1.2;">${{h.name}}</div>
                  <div style="font-size: 10.5px; color: #94a3b8; margin-bottom: 8px;">${{h.district}} &bull; ${{h.incidents}} Police Reports</div>
                  <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 6px 8px; font-size: 11px; margin-bottom: 8px;">
                    <div style="color: #cbd5e1; margin-bottom: 2px;"><b>Crime:</b> ${{h.crime}}</div>
                    <div style="color: #cbd5e1;"><b>Premises:</b> ${{h.premises}}</div>
                  </div>
                  <button onclick="map.flyTo([${{h.lat}}, ${{h.lon}}], 16, {{duration: 1}})" style="width: 100%; background: #0284c7; border: 1px solid #38bdf8; color: #fff; border-radius: 6px; padding: 5px 8px; font-size: 11px; font-weight: 700; cursor: pointer;">
                    🔍 Zoom into Cluster Core
                  </button>
                  <button onclick="startNavigationTo(${{h.lat}}, ${{h.lon}}, '${{h.name.replace(/'/g, \"\\\\'\")}}', false)" style="width: 100%; box-sizing: border-box; background: linear-gradient(135deg, #0284c7, #4f46e5); border: 1px solid #38bdf8; color: #fff; border-radius: 6px; padding: 6px 8px; font-size: 11px; font-weight: 800; cursor: pointer; margin-top: 6px; display: flex; align-items: center; justify-content: center; gap: 5px; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);">
                    🧭 Navigate Here (Live Street ETA & Turns)
                  </button>
                  <a href="https://www.mapillary.com/app/?lat=${{h.lat}}&lng=${{h.lon}}&z=17" target="_blank" style="display: block; text-align: center; width: 100%; box-sizing: border-box; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; border-radius: 6px; padding: 5px 8px; font-size: 10.5px; font-weight: 700; text-decoration: none; margin-top: 6px;">
                    📸 Free 360° Street View (Mapillary)
                  </a>
                </div>
              </div>
            `);
          }});
          
          if (filter === 'ALL' || filter === 'SAFE') {{
            SAFE_ZONES.forEach(s => {{
              L.circle([s.lat, s.lon], {{
                radius: 420,
                color: '#10b981',
                weight: 1.5,
                fillColor: '#34d399',
                fillOpacity: 0.18
              }}).addTo(markersGroup);
              
              const safeIcon = L.divIcon({{
                html: `
                  <div style="display:flex; flex-direction:column; align-items:center; cursor:pointer;">
                    <div style="width:28px; height:28px; border-radius:50%; background:#059669; box-shadow:0 0 12px #10b981; display:flex; align-items:center; justify-content:center; font-size:13px; color:#fff; border: 2px solid #fff;">
                      🛡️
                    </div>
                    <div style="font-size:9.5px; font-weight:800; background:#064e3b; color:#6ee7b7; border:1px solid #10b981; padding:1px 6px; border-radius:4px; margin-top:2px; white-space:nowrap; box-shadow: 0 2px 8px rgba(0,0,0,0.5);">
                      Safe Corridor
                    </div>
                  </div>
                `,
                className: '',
                iconSize: [42, 42],
                iconAnchor: [21, 21]
              }});
              const sm = L.marker([s.lat, s.lon], {{ icon: safeIcon }}).addTo(markersGroup);
              sm.bindPopup(`
                <div style="width: 250px; font-family: -apple-system, sans-serif;">
                  <div style="position: relative; height: 110px; width: 100%; overflow: hidden; background: #064e3b;">
                    <img src="${{s.image}}" alt="${{s.name}}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'" />
                    <div style="position: absolute; top: 8px; left: 8px; background: #059669; color: #fff; font-size: 9.5px; font-weight: 800; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase;">
                      🛡️ VERIFIED SAFE CORRIDOR
                    </div>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 35px; background: linear-gradient(to top, #0b0f19, transparent);"></div>
                  </div>
                  <div style="padding: 10px 12px;">
                    <div style="font-size: 13px; font-weight: 800; color: #f8fafc; margin-bottom: 2px;">${{s.name}}</div>
                    <div style="font-size: 10.5px; color: #6ee7b7; margin-bottom: 6px;">${{s.district}} &bull; Threat &lt; 20%</div>
                    <div style="background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 6px; padding: 6px 8px; font-size: 11px; color: #a7f3d0; margin-bottom: 8px;">
                      ${{s.desc}}
                    </div>
                    <button onclick="map.flyTo([${{s.lat}}, ${{s.lon}}], 16, {{duration: 1}})" style="width: 100%; background: #059669; border: 1px solid #10b981; color: #fff; border-radius: 6px; padding: 5px 8px; font-size: 11px; font-weight: 700; cursor: pointer;">
                      🛡️ Center on Safe Haven
                    </button>
                    <button onclick="startNavigationTo(${{s.lat}}, ${{s.lon}}, '${{s.name.replace(/'/g, \"\\\\'\")}}', false)" style="width: 100%; box-sizing: border-box; background: linear-gradient(135deg, #059669, #10b981); border: 1px solid #34d399; color: #fff; border-radius: 6px; padding: 6px 8px; font-size: 11px; font-weight: 800; cursor: pointer; margin-top: 6px; display: flex; align-items: center; justify-content: center; gap: 5px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
                      🛡️ Route Safe Corridor (Turn-by-Turn)
                    </button>
                  </div>
                </div>
              `);
            }});
          }}
        }}
        
        // PREDICTIVE AUTOCOMPLETE SEARCH SYSTEM
        let searchMarker = null;
        let searchDebounceTimer = null;
        const searchInput = document.getElementById('mapSearchInput');
        const searchDropdown = document.getElementById('predictiveDropdown');
        const clearBtn = document.getElementById('searchClearBtn');
        let selectedIndex = -1;
        let currentSuggestions = [];
        
        function renderSuggestions(list) {{
          currentSuggestions = list;
          selectedIndex = -1;
          
          if (!list || list.length === 0) {{
            searchDropdown.innerHTML = `<div style="padding: 12px; font-size: 11px; color: #94a3b8; text-align: center;">No matching locations found in Delhi</div>`;
            searchDropdown.style.display = 'block';
            return;
          }}
          
          let html = `<div class="dropdown-header">MATCHING LOCATIONS IN DELHI NCT</div>`;
          list.forEach((item, idx) => {{
            html += `
              <div class="dropdown-item" id="sugg-item-${{idx}}" onclick="selectSuggestion(${{idx}})">
                <span class="dropdown-icon">${{item.badgeClass === 'badge-danger' ? '🚨' : (item.badgeClass === 'badge-safe' ? '🛡️' : '📍')}}</span>
                <div class="dropdown-info">
                  <div class="dropdown-title">${{item.name}}</div>
                  <div class="dropdown-subtitle">${{item.district}}</div>
                </div>
                ${{item.badge ? `<span class="dropdown-badge ${{item.badgeClass}}">${{item.badge}}</span>` : ''}}
              </div>
            `;
          }});
          
          searchDropdown.innerHTML = html;
          searchDropdown.style.display = 'block';
        }}
        
        function getPredictiveMatches(query) {{
          const q = query.trim().toLowerCase();
          if (!q) return [];
          
          // Match local high-priority index first (0ms instantaneous response!)
          const localMatches = DELHI_LOCATIONS.filter(loc => 
            loc.name.toLowerCase().includes(q) || 
            loc.district.toLowerCase().includes(q)
          );
          return localMatches;
        }}
        
        async function fetchNominatimMatches(query) {{
          try {{
            const q = query.trim().toLowerCase();
            const searchTerm = q.includes('delhi') ? q : q + ' Delhi';
            const url = 'https://nominatim.openstreetmap.org/search?format=json&countrycodes=in&viewbox=76.8,28.4,77.4,28.9&bounded=0&limit=5&q=' + encodeURIComponent(searchTerm);
            const res = await fetch(url);
            const data = await res.json();
            
            if (data && data.length > 0) {{
              return data.map(d => ({{
                name: d.display_name.split(',')[0],
                district: d.display_name.split(',').slice(1, 4).join(',').trim(),
                lat: parseFloat(d.lat),
                lon: parseFloat(d.lon),
                badge: 'OpenStreetMap',
                badgeClass: 'badge-transit'
              }}));
            }}
          }} catch (e) {{
            console.warn('OSM search error:', e);
          }}
          return [];
        }}
        
        searchInput.addEventListener('input', (e) => {{
          const query = e.target.value;
          clearBtn.style.display = query ? 'block' : 'none';
          
          if (!query.trim()) {{
            searchDropdown.style.display = 'none';
            return;
          }}
          
          // 1. Instant local match
          const localMatches = getPredictiveMatches(query);
          renderSuggestions(localMatches);
          
          // 2. Debounce remote search to complement suggestions
          if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
          searchDebounceTimer = setTimeout(async () => {{
            const remoteMatches = await fetchNominatimMatches(query);
            if (remoteMatches && remoteMatches.length > 0) {{
              // Merge & deduplicate by name
              const names = new Set(localMatches.map(m => m.name.toLowerCase()));
              const combined = [...localMatches];
              remoteMatches.forEach(rm => {{
                if (!names.has(rm.name.toLowerCase())) {{
                  combined.push(rm);
                  names.add(rm.name.toLowerCase());
                }}
              }});
              renderSuggestions(combined.slice(0, 7));
            }}
          }}, 250);
        }});
        
        // Keyboard navigation for autocomplete list
        searchInput.addEventListener('keydown', (e) => {{
          if (searchDropdown.style.display === 'none') {{
            if (e.key === 'Enter') executeSearch();
            return;
          }}
          
          if (e.key === 'ArrowDown') {{
            e.preventDefault();
            if (currentSuggestions.length > 0) {{
              selectedIndex = (selectedIndex + 1) % currentSuggestions.length;
              highlightSelectedItem();
            }}
          }} else if (e.key === 'ArrowUp') {{
            e.preventDefault();
            if (currentSuggestions.length > 0) {{
              selectedIndex = (selectedIndex - 1 + currentSuggestions.length) % currentSuggestions.length;
              highlightSelectedItem();
            }}
          }} else if (e.key === 'Enter') {{
            e.preventDefault();
            if (selectedIndex >= 0 && selectedIndex < currentSuggestions.length) {{
              selectSuggestion(selectedIndex);
            }} else {{
              executeSearch();
            }}
          }} else if (e.key === 'Escape') {{
            searchDropdown.style.display = 'none';
          }}
        }});
        
        function highlightSelectedItem() {{
          document.querySelectorAll('.dropdown-item').forEach((el, idx) => {{
            el.classList.toggle('active-item', idx === selectedIndex);
          }});
        }}
        
        window.selectSuggestion = function(idx) {{
          const item = currentSuggestions[idx];
          if (!item) return;
          
          searchInput.value = item.name;
          searchDropdown.style.display = 'none';
          clearBtn.style.display = 'block';
          
          focusLocationOnMap(item.lat, item.lon, item.name, item.district);
        }};
        
        window.clearSearchInput = function() {{
          searchInput.value = '';
          searchDropdown.style.display = 'none';
          clearBtn.style.display = 'none';
          if (searchMarker) {{
            map.removeLayer(searchMarker);
            searchMarker = null;
          }}
        }};
        
        window.executeSearch = function() {{
          const query = searchInput.value.trim();
          if (!query) return;
          
          // Check if matches local top item
          const local = getPredictiveMatches(query);
          if (local.length > 0) {{
            focusLocationOnMap(local[0].lat, local[0].lon, local[0].name, local[0].district);
            searchDropdown.style.display = 'none';
            return;
          }}
          
          // Otherwise fetch remote
          const btn = document.getElementById('searchActionBtn');
          btn.innerText = '⌛';
          btn.disabled = true;
          
          fetchNominatimMatches(query).then(matches => {{
            btn.innerText = 'Search';
            btn.disabled = false;
            if (matches && matches.length > 0) {{
              focusLocationOnMap(matches[0].lat, matches[0].lon, matches[0].name, matches[0].district);
              searchDropdown.style.display = 'none';
            }} else {{
              alert('Location not found in Delhi. Try typing "Rajiv Chowk", "Dwarka", or "Hauz Khas".');
            }}
          }});
        }};
        
        function focusLocationOnMap(lat, lon, title, subtitle) {{
          if (searchMarker) map.removeLayer(searchMarker);
          
          const sIcon = L.divIcon({{
            html: `
              <div style="display:flex; flex-direction:column; align-items:center;">
                <div style="width:34px; height:34px; border-radius:50%; background: linear-gradient(135deg, #0284c7, #10b981); box-shadow: 0 0 20px #38bdf8; display:flex; align-items:center; justify-content:center; font-size:17px; border: 2px solid #fff;">
                  📍
                </div>
                <div style="background:#0b0f19; color:#38bdf8; border:1px solid #0284c7; border-radius:4px; font-size:10px; font-weight:800; padding:2px 6px; margin-top:2px; white-space:nowrap; max-width:140px; overflow:hidden; text-overflow:ellipsis; box-shadow: 0 4px 10px rgba(0,0,0,0.6);">
                  ${{title}}
                </div>
              </div>
            `,
            className: '',
            iconSize: [40, 48],
            iconAnchor: [20, 24]
          }});
          
          searchMarker = L.marker([lat, lon], {{ icon: sIcon, zIndexOffset: 950 }}).addTo(map);
          searchMarker.bindPopup(`
            <div style="width: 230px; padding: 10px 12px; font-family: -apple-system, sans-serif;">
              <span style="color: #38bdf8; font-size: 10.5px; font-weight: 800; text-transform: uppercase;">📍 TARGET LOCATION</span>
              <h4 style="margin: 4px 0 2px 0; font-size: 13px; color: #fff;">${{title}}</h4>
              <p style="color: #94a3b8; font-size: 11px; margin: 2px 0 8px 0;">${{subtitle || 'Delhi NCT'}}</p>
              <button onclick="updateUserPosition(${{lat}}, ${{lon}}, 15); map.flyTo([${{lat}}, ${{lon}}], 16);" style="width:100%; background:#0284c7; border:1px solid #38bdf8; color:#fff; border-radius:6px; padding:5px 8px; font-size:11px; font-weight:700; cursor:pointer;">
                🎯 Set as My Location
              </button>
              <button onclick="startNavigationTo(${{lat}}, ${{lon}}, '${{title.replace(/'/g, \"\\\\'\")}}', false)" style="width:100%; box-sizing:border-box; background:linear-gradient(135deg, #0284c7, #4f46e5); border:1px solid #38bdf8; color:#fff; border-radius:6px; padding:6px 8px; font-size:11px; font-weight:800; cursor:pointer; margin-top:6px; display:flex; align-items:center; justify-content:center; gap:5px;">
                🧭 Navigate Here (Turn-by-Turn)
              </button>
            </div>
          `).openPopup();
          
          map.flyTo([lat, lon], 16, {{ duration: 1.2 }});
        }}
        
        // Hide dropdown on click outside
        document.addEventListener('click', (e) => {{
          if (!e.target.closest('.search-container')) {{
            searchDropdown.style.display = 'none';
          }}
        }});
        
        function updateUserPosition(lat, lon, accuracy, isNavigating) {{
          const prevLat = currentUserPos.lat;
          const prevLon = currentUserPos.lon;
          currentUserPos = {{ lat, lon }};
          
          const distMoved = calcDistMeters(prevLat, prevLon, lat, lon);
          if (isNavigating || (distMoved > 2 && distMoved < 500)) {{
            trailWaypoints.push([lat, lon]);
            if (trailWaypoints.length > 250) trailWaypoints.shift();
            trailPolyline.setLatLngs(trailWaypoints);
          }} else if (distMoved >= 500 && !isNavigating) {{
            // Teleported or clicked distant pin: reset trail to avoid drawing straight lines across Delhi!
            trailWaypoints = [[lat, lon]];
            trailPolyline.setLatLngs(trailWaypoints);
          }}
          
          document.getElementById('gpsCoordsText').innerText = `${{lat.toFixed(4)}}°N, ${{lon.toFixed(4)}}°E`;
          document.getElementById('gpsAccText').innerText = `&plusmn;${{Math.round(accuracy)}}m`;
          
          let closest = null;
          let minDist = Infinity;
          HOTSPOTS.forEach(h => {{
            const d = calcDistMeters(lat, lon, h.lat, h.lon);
            if (d < minDist) {{
              minDist = d;
              closest = h;
            }}
          }});
          
          const badge = document.getElementById('threatBadge');
          const txt = document.getElementById('closestHotspotText');
          
          if (minDist <= 400 && closest.riskLevel === 'HIGH') {{
            badge.className = 'threat-tag tag-high';
            badge.innerText = '🚨 DANGER';
            txt.innerHTML = `Within <b>${{minDist}}m</b> of ${{closest.name.split(' - ')[1] || closest.name}} (${{Math.round(closest.riskScore*100)}}%)`;
          }} else if (minDist <= 750) {{
            badge.className = 'threat-tag tag-med';
            badge.innerText = '⚠️ CAUTION';
            txt.innerHTML = `Within <b>${{minDist}}m</b> of ${{closest.name.split(' - ')[1] || closest.name}}`;
          }} else {{
            badge.className = 'threat-tag tag-safe';
            badge.innerText = '🛡️ SAFE BUFFER';
            txt.innerHTML = `Nearest hotspot: <b>${{(minDist/1000).toFixed(2)}} km</b> (${{closest.name.split(' ')[0]}})`;
          }}
          
          const userRadarHtml = `
            <div style="position:relative; display:flex; align-items:center; justify-content:center;">
              <div class="radar-pulse-marker" style="width:24px; height:24px; border-radius:50%; background:#06b6d4; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:12px;">
                📍
              </div>
            </div>
          `;
          const radarIcon = L.divIcon({{ html: userRadarHtml, className: '', iconSize: [26, 26], iconAnchor: [13, 13] }});
          
          if (!userMarker) {{
            userMarker = L.marker([lat, lon], {{ icon: radarIcon, zIndexOffset: 1000 }}).addTo(map);
            userMarker.bindTooltip('<b>📍 Live Movement</b><br/>You are here', {{ permanent: false }});
          }} else {{
            userMarker.setLatLng([lat, lon]);
          }}
          
          if (!userAccuracyCircle) {{
            userAccuracyCircle = L.circle([lat, lon], {{
              radius: Math.max(accuracy, 50),
              color: '#06b6d4',
              weight: 1,
              fillColor: '#22d3ee',
              fillOpacity: 0.12
            }}).addTo(map);
          }} else {{
            userAccuracyCircle.setLatLng([lat, lon]);
            userAccuracyCircle.setRadius(Math.max(accuracy, 50));
          }}
          
          map.panTo([lat, lon], {{ animate: true, duration: 0.8 }});
        }}
        
        // ==========================================
        // REAL-TIME STREET ROUTING & NAVIGATION (OSRM)
        // ==========================================
        let currentNavRoute = null;
        let navRoutePolyline = null;
        let navRouteCasing = null;
        let navDestMarker = null;
        let navDriveTimer = null;
        let navDriveIdx = 0;
        let isDriving = false;

        function getManeuverIcon(maneuver) {{
          if (!maneuver) return '⬆';
          const type = maneuver.type || '';
          const mod = (maneuver.modifier || '').toLowerCase();
          
          if (type === 'arrive') return '🏁';
          if (type === 'depart') return '🚗';
          if (type === 'rotary' || type === 'roundabout') return '🔄';
          if (mod.includes('sharp left')) return '⮢';
          if (mod.includes('slight left')) return '⮤';
          if (mod.includes('left')) return '↰';
          if (mod.includes('sharp right')) return '⮣';
          if (mod.includes('slight right')) return '⮥';
          if (mod.includes('right')) return '↱';
          if (mod.includes('u-turn')) return '↶';
          return '⬆';
        }}

        function formatManeuverText(step) {{
          if (!step || !step.maneuver) return 'Proceed along corridor';
          const type = step.maneuver.type || '';
          const mod = step.maneuver.modifier || '';
          const road = step.name ? `onto <b>${{step.name}}</b>` : 'along road';
          
          if (type === 'arrive') return `🏁 Arrive at destination (${{step.name || 'Target'}})`;
          if (type === 'depart') return `Head ${{mod || 'straight'}} ${{road}}`;
          if (type === 'roundabout' || type === 'rotary') return `Take roundabout ${{road}}`;
          if (type === 'end of road') return `Turn ${{mod}} at end of road ${{road}}`;
          if (type === 'fork') return `Keep ${{mod}} at fork ${{road}}`;
          if (mod) return `Turn ${{mod}} ${{road}}`;
          return `Continue ${{road}}`;
        }}

        function formatDist(meters) {{
          if (meters < 1000) return `${{Math.round(meters)}} m`;
          return `${{(meters / 1000).toFixed(1)}} km`;
        }}

        function formatDuration(seconds) {{
          const mins = Math.ceil(seconds / 60);
          if (mins < 60) return `${{mins}} min`;
          const hrs = Math.floor(mins / 60);
          const rem = mins % 60;
          return `${{hrs}} hr ${{rem}} min`;
        }}

        function generateCorridorInterpolation(p1, p2) {{
          const pts = [];
          const numSteps = 45;
          for (let i = 0; i <= numSteps; i++) {{
            const t = i / numSteps;
            const lat = p1[0] + (p2[0] - p1[0]) * t;
            const lon = p1[1] + (p2[1] - p1[1]) * t;
            const curve = Math.sin(t * Math.PI) * 0.003;
            pts.push([lat + curve, lon + curve]);
          }}
          return pts;
        }}

        window.startNavigationTo = async function(destLat, destLon, destName, autoDrive) {{
          const startLat = currentUserPos.lat;
          const startLon = currentUserPos.lon;
          
          // Display HUD loading
          const hud = document.getElementById('navHud');
          hud.style.display = 'block';
          document.getElementById('navManeuverIcon').innerText = '⌛';
          document.getElementById('navInstruction').innerHTML = `Calculating street route to <b>${{destName}}</b>...`;
          document.getElementById('navNextStreet').innerText = 'Querying OpenStreetMap Delhi Road Network (OSRM)...';
          document.getElementById('navDistText').innerText = '--';
          document.getElementById('navEtaText').innerText = '--';
          
          try {{
            // Real-time Street Navigation API (100% Free OpenStreetMap / OSRM)
            const url = `https://router.project-osrm.org/route/v1/driving/${{startLon}},${{startLat}};${{destLon}},${{destLat}}?overview=full&geometries=geojson&steps=true`;
            const resp = await fetch(url);
            const data = await resp.json();
            
            if (data.code === 'Ok' && data.routes && data.routes.length > 0) {{
              const r = data.routes[0];
              const coords = r.geometry.coordinates.map(c => [c[1], c[0]]); // [lon, lat] -> [lat, lon]
              const steps = r.legs[0]?.steps || [];
              displayStreetRoute(coords, steps, r.distance, r.duration, destName, [destLat, destLon], autoDrive);
            }} else {{
              throw new Error('OSRM routing response not ok');
            }}
          }} catch (err) {{
            console.warn('OSRM query failed or offline, using fallback corridor:', err);
            const fallbackPoints = generateCorridorInterpolation([startLat, startLon], [destLat, destLon]);
            const estDist = calcDistMeters(startLat, startLon, destLat, destLon) * 1.28;
            const estDuration = (estDist / 8.5); // ~30 km/h
            const fallbackSteps = [
              {{ maneuver: {{ type: 'depart', modifier: 'straight' }}, name: 'Current Corridor', distance: estDist * 0.35, duration: estDuration * 0.35 }},
              {{ maneuver: {{ type: 'turn', modifier: 'slight right' }}, name: 'Delhi Ring Road Highway', distance: estDist * 0.45, duration: estDuration * 0.45 }},
              {{ maneuver: {{ type: 'arrive', modifier: '' }}, name: destName, distance: estDist * 0.2, duration: estDuration * 0.2 }}
            ];
            displayStreetRoute(fallbackPoints, fallbackSteps, estDist, estDuration, destName, [destLat, destLon], autoDrive);
          }}
        }};

        function displayStreetRoute(coords, steps, totalDistMeters, totalDurationSec, destName, destLatLng, autoDrive) {{
          clearNavigationRoute(false);
          
          currentNavRoute = {{
            coords: coords,
            steps: steps,
            totalDistMeters: totalDistMeters,
            totalDurationSec: totalDurationSec,
            destName: destName,
            destLatLng: destLatLng
          }};
          navDriveIdx = 0;
          
          // Clear old straight trail
          trailWaypoints = [coords[0]];
          trailPolyline.setLatLngs(trailWaypoints);
          
          // Outer black casing line
          navRouteCasing = L.polyline(coords, {{
            color: '#030712',
            weight: 8,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
          }}).addTo(map);
          
          // Inner glowing cyan street line snapped to roads
          navRoutePolyline = L.polyline(coords, {{
            color: '#00f0ff',
            weight: 4.5,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
          }}).addTo(map);
          
          // Destination Flag
          const flagHtml = `
            <div style="display:flex; flex-direction:column; align-items:center;">
              <div style="width:34px; height:34px; border-radius:50%; background:#ef4444; border:2px solid #fff; box-shadow:0 0 16px #ef4444; display:flex; align-items:center; justify-content:center; font-size:16px;">
                🏁
              </div>
              <div style="background:#0b0f19; color:#fff; border:1px solid #ef4444; border-radius:4px; font-size:10px; font-weight:800; padding:2px 6px; margin-top:2px; white-space:nowrap; box-shadow:0 4px 10px rgba(0,0,0,0.6);">
                ${{destName.split(' ')[0]}}
              </div>
            </div>
          `;
          const flagIcon = L.divIcon({{ html: flagHtml, className: '', iconSize: [36, 46], iconAnchor: [18, 23] }});
          navDestMarker = L.marker(destLatLng, {{ icon: flagIcon, zIndexOffset: 990 }}).addTo(map);
          
          // Zoom to show whole route
          const bounds = L.latLngBounds(coords);
          map.fitBounds(bounds, {{ padding: [70, 70], animate: true, duration: 1.0 }});
          
          // Populate HUD & Drawer
          updateNavHUD(0);
          populateNavStepsDrawer(steps);
          document.getElementById('navHud').style.display = 'block';
          
          if (autoDrive) {{
            setTimeout(() => toggleNavDriveSim(), 600);
          }}
        }}

        function updateNavHUD(stepIdx) {{
          if (!currentNavRoute || !currentNavRoute.steps || currentNavRoute.steps.length === 0) return;
          const steps = currentNavRoute.steps;
          const cur = steps[stepIdx] || steps[0];
          const nxt = steps[stepIdx + 1];
          
          const icon = getManeuverIcon(cur.maneuver);
          const mainText = formatManeuverText(cur);
          const subText = nxt ? `In ${{formatDist(cur.distance)}}, ${{formatManeuverText(nxt).replace(/<[^>]*>/g, '')}}` : `Approaching ${{currentNavRoute.destName}}`;
          
          document.getElementById('navManeuverIcon').innerText = icon;
          document.getElementById('navInstruction').innerHTML = mainText;
          document.getElementById('navNextStreet').innerText = subText;
          
          const mins = Math.ceil(currentNavRoute.totalDurationSec / 60);
          const arrival = new Date(Date.now() + currentNavRoute.totalDurationSec * 1000).toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }});
          document.getElementById('navEtaText').innerText = `${{mins}} min (${{arrival}})`;
          document.getElementById('navDistText').innerText = formatDist(currentNavRoute.totalDistMeters);
        }}

        function findAndDisplayCurrentManeuver(lat, lon) {{
          if (!currentNavRoute || !currentNavRoute.steps) return;
          const steps = currentNavRoute.steps;
          let closestIdx = 0;
          let minDist = Infinity;
          for (let i = 0; i < steps.length; i++) {{
            const loc = steps[i].maneuver?.location;
            if (loc) {{
              const d = calcDistMeters(lat, lon, loc[1], loc[0]);
              if (d < minDist) {{
                minDist = d;
                closestIdx = i;
              }}
            }}
          }}
          updateNavHUD(closestIdx);
          
          const items = document.querySelectorAll('.nav-step-item');
          items.forEach((el, idx) => el.classList.toggle('active', idx === closestIdx));
        }}

        function populateNavStepsDrawer(steps) {{
          const list = document.getElementById('navStepsList');
          if (!list) return;
          list.innerHTML = '';
          
          document.getElementById('navDrawerSummary').innerText = `${{formatDist(currentNavRoute.totalDistMeters)}} • ${{formatDuration(currentNavRoute.totalDurationSec)}}`;
          
          steps.forEach((s, idx) => {{
            const icon = getManeuverIcon(s.maneuver);
            const text = formatManeuverText(s);
            const dist = formatDist(s.distance);
            
            const row = document.createElement('div');
            row.className = `nav-step-item ${{idx === 0 ? 'active' : ''}}`;
            row.innerHTML = `
              <span class="nav-step-icon">${{icon}}</span>
              <span class="nav-step-desc"><b>${{idx + 1}}.</b> ${{text}}</span>
              <span class="nav-step-dist">${{dist}}</span>
            `;
            row.onclick = () => {{
              if (s.maneuver?.location) {{
                map.flyTo([s.maneuver.location[1], s.maneuver.location[0]], 17, {{ duration: 1.0 }});
              }}
            }};
            list.appendChild(row);
          }});
        }}

        window.toggleNavStepsDrawer = function() {{
          const drawer = document.getElementById('navStepsDrawer');
          drawer.style.display = drawer.style.display === 'none' ? 'block' : 'none';
        }};

        window.toggleNavDriveSim = function() {{
          if (!currentNavRoute) return;
          const btn = document.getElementById('navSimPlayBtn');
          const simTopBtn = document.getElementById('btnSim');
          
          if (isDriving) {{
            clearInterval(navDriveTimer);
            navDriveTimer = null;
            isDriving = false;
            btn.innerText = '▶ Drive';
            btn.classList.remove('active');
            if (simTopBtn) {{
              simTopBtn.innerText = '🚀 Sim GPS';
              simTopBtn.classList.remove('active');
            }}
          }} else {{
            isDriving = true;
            btn.innerText = '⏸ Pause';
            btn.classList.add('active');
            if (simTopBtn) {{
              simTopBtn.innerText = '⏹️ Stop Sim';
              simTopBtn.classList.add('active');
            }}
            
            const coords = currentNavRoute.coords;
            navDriveTimer = setInterval(() => {{
              if (navDriveIdx >= coords.length - 1) {{
                clearInterval(navDriveTimer);
                navDriveTimer = null;
                isDriving = false;
                btn.innerText = '🏁 Arrived';
                btn.classList.remove('active');
                if (simTopBtn) {{
                  simTopBtn.innerText = '🚀 Sim GPS';
                  simTopBtn.classList.remove('active');
                }}
                document.getElementById('navInstruction').innerHTML = `🏁 Arrived at <b>${{currentNavRoute.destName}}</b>`;
                document.getElementById('navManeuverIcon').innerText = '🏁';
                document.getElementById('navNextStreet').innerText = 'Destination reached via Delhi street network';
                document.getElementById('navDistText').innerText = '0 m';
                document.getElementById('navEtaText').innerText = '0 min';
                return;
              }}
              
              navDriveIdx += 1;
              const p = coords[navDriveIdx];
              updateUserPosition(p[0], p[1], 10, true);
              
              const ratio = navDriveIdx / coords.length;
              const remDist = Math.max(0, currentNavRoute.totalDistMeters * (1 - ratio));
              const remSec = Math.max(0, currentNavRoute.totalDurationSec * (1 - ratio));
              document.getElementById('navDistText').innerText = formatDist(remDist);
              document.getElementById('navEtaText').innerText = `${{Math.ceil(remSec / 60)}} min`;
              
              findAndDisplayCurrentManeuver(p[0], p[1]);
            }}, 120);
          }}
        }};

        window.clearNavigationRoute = function(clearUI) {{
          if (navDriveTimer) {{
            clearInterval(navDriveTimer);
            navDriveTimer = null;
          }}
          isDriving = false;
          navDriveIdx = 0;
          if (navRoutePolyline) {{ map.removeLayer(navRoutePolyline); navRoutePolyline = null; }}
          if (navRouteCasing) {{ map.removeLayer(navRouteCasing); navRouteCasing = null; }}
          if (navDestMarker) {{ map.removeLayer(navDestMarker); navDestMarker = null; }}
          currentNavRoute = null;
          
          if (clearUI) {{
            document.getElementById('navHud').style.display = 'none';
            document.getElementById('navStepsDrawer').style.display = 'none';
            const btn = document.getElementById('btnSim');
            if (btn) {{ btn.innerText = '🚀 Sim GPS'; btn.classList.remove('active'); }}
          }}
        }};

        window.openQuickRouteModal = function() {{
          populateQuickRouteModal();
          document.getElementById('quickRouteModal').style.display = 'flex';
        }};
        
        window.closeQuickRouteModal = function() {{
          document.getElementById('quickRouteModal').style.display = 'none';
        }};
        
        function populateQuickRouteModal() {{
          const container = document.getElementById('quickRouteList');
          if (!container) return;
          container.innerHTML = '';
          
          const targets = [
            {{ name: "Rajiv Chowk Metro (Connaught Place)", lat: 28.6328, lon: 77.2197, type: "🚨 Hotspot Centroid", badgeClass: "color:#ef4444;" }},
            {{ name: "Kashmere Gate ISBT & Terminal", lat: 28.6675, lon: 77.2285, type: "🚨 Critical Hotspot", badgeClass: "color:#ef4444;" }},
            {{ name: "Chanakyapuri Diplomatic Enclave", lat: 28.5983, lon: 77.1912, type: "🛡️ Safe Haven", badgeClass: "color:#10b981;" }},
            {{ name: "India Gate & Kartavya Path", lat: 28.6129, lon: 77.2295, type: "🛡️ Safe Corridor", badgeClass: "color:#10b981;" }},
            {{ name: "Hauz Khas Village & Lake", lat: 28.5535, lon: 77.1945, type: "🏙️ Lifestyle & Market", badgeClass: "color:#38bdf8;" }},
            {{ name: "Seelampur Market Corridor", lat: 28.6644, lon: 77.2711, type: "🚨 Critical Corridor", badgeClass: "color:#ef4444;" }},
            {{ name: "Civil Lines VIP & Raj Niwas", lat: 28.6820, lon: 77.2180, type: "🛡️ Secure Enclave", badgeClass: "color:#10b981;" }},
            {{ name: "Anand Vihar Terminal", lat: 28.6469, lon: 77.3160, type: "🚨 East Hotspot", badgeClass: "color:#ef4444;" }},
            {{ name: "Saket Select Citywalk", lat: 28.5284, lon: 77.2185, type: "🛍️ Commercial Corridor", badgeClass: "color:#38bdf8;" }}
          ];
          
          targets.forEach(t => {{
            const distM = calcDistMeters(currentUserPos.lat, currentUserPos.lon, t.lat, t.lon);
            const distStr = formatDist(distM);
            const estMin = Math.ceil((distM * 1.25) / 500);
            
            const div = document.createElement('div');
            div.className = 'quick-route-item';
            div.innerHTML = `
              <div>
                <div style="font-size:12.5px; font-weight:800; color:#fff;">${{t.name}}</div>
                <div style="font-size:10.5px; ${{t.badgeClass}} font-weight:700;">${{t.type}}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:12px; font-family:monospace; color:#38bdf8; font-weight:800;">${{distStr}}</div>
                <div style="font-size:10px; color:#94a3b8;">~${{estMin}} mins</div>
              </div>
            `;
            div.onclick = () => {{
              closeQuickRouteModal();
              startNavigationTo(t.lat, t.lon, t.name, false);
            }};
            container.appendChild(div);
          }});
        }}

        // Right-click map to route anywhere
        map.on('contextmenu', (e) => {{
          startNavigationTo(e.latlng.lat, e.latlng.lng, `Location (${{e.latlng.lat.toFixed(3)}}, ${{e.latlng.lng.toFixed(3)}})`, false);
        }});
        
        // Initial setup
        renderZones('ALL');
        updateUserPosition({init_lat}, {init_lon}, 20);
        
        if (navigator.geolocation) {{
          navigator.geolocation.watchPosition(
            pos => {{
              updateUserPosition(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy);
            }},
            err => {{
              console.warn('GPS error:', err.message);
            }},
            {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 1000 }}
          );
        }}
        
        window.setLayerFilter = function(f) {{
          activeFilter = f;
          document.getElementById('btnAll').classList.toggle('active', f === 'ALL');
          document.getElementById('btnHigh').classList.toggle('active', f === 'HIGH');
          document.getElementById('btnSafe').classList.toggle('active', f === 'SAFE');
          renderZones(f);
        }};
        
        window.centerOnMe = function() {{
          map.flyTo([currentUserPos.lat, currentUserPos.lon], 15, {{ duration: 1.2 }});
        }};
        
        window.zoomInMap = function() {{
          map.zoomIn();
        }};
        
        window.zoomOutMap = function() {{
          map.zoomOut();
        }};
        
        window.resetZoomMap = function() {{
          map.setView([currentUserPos.lat, currentUserPos.lon], {init_zoom}, {{ animate: true, duration: 0.8 }});
        }};
        
        window.fitAllHotspots = function() {{
          if (HOTSPOTS && HOTSPOTS.length > 0) {{
            const bounds = L.latLngBounds(HOTSPOTS.map(h => [h.lat, h.lon]));
            map.fitBounds(bounds, {{ padding: [60, 60], animate: true, duration: 1.0 }});
          }}
        }};
        
        function updateZoomDisplay() {{
          const z = map.getZoom();
          let zLabel = `${{z}}x`;
          if (z <= 11) zLabel += " (City)";
          else if (z <= 13) zLabel += " (District)";
          else if (z <= 15) zLabel += " (Corridor)";
          else zLabel += " (Street)";
          
          const dock = document.getElementById('zoomLevelDock');
          if (dock) dock.innerText = `${{z}}x`;
          const text = document.getElementById('gpsZoomText');
          if (text) text.innerText = zLabel;
        }}
        
        map.on('zoomend', updateZoomDisplay);
        updateZoomDisplay();
        
        window.addEventListener('keydown', (e) => {{
          if (e.target.tagName === 'INPUT') return;
          if (e.key === '+' || e.key === '=') zoomInMap();
          else if (e.key === '-' || e.key === '_') zoomOutMap();
          else if (e.key === '0') resetZoomMap();
          else if (e.key.toLowerCase() === 'f') fitAllHotspots();
        }});
        
        window.toggleSimulation = function() {{
          const btn = document.getElementById('btnSim');
          if (isDriving || navDriveTimer) {{
            toggleNavDriveSim();
            btn.innerText = '🚀 Sim GPS';
            btn.classList.remove('active');
            return;
          }}
          
          btn.innerText = '⏹️ Stop Sim';
          btn.classList.add('active');
          
          if (currentNavRoute) {{
            toggleNavDriveSim();
            return;
          }}
          
          // Auto-start real road navigation to Rajiv Chowk Metro Hotspot!
          startNavigationTo(28.6328, 77.2197, "Rajiv Chowk Metro (Connaught Place)", true);
        }};
      </script>
    </body>
    </html>
    """
    return html_code



def create_google_maps_sentinel_html(hotspots_df=None, initial_user_lat=None, initial_user_lon=None, initial_zoom=13, incidents_df=None, api_key=None):
    """
    Renders an interactive Google Maps Platform Sentinel experience:
    - Google Maps JavaScript API with dynamic library bootstrap loader
    - Mandatory internalUsageAttributionIds: ['gmp_git_agentskills_v1']
    - Custom High-Contrast Cruip Dark Vector Map Style
    - Satellite & Hybrid toggle, Street View Pegman, and Real-time Traffic Layer
    - DBSCAN Hotspot Circles with InfoWindows and Landmark Imagery
    - Live Geolocation watchPosition tracking with pulse animation
    - Google Places Autocomplete search input
    - Crime density heatmap overlay using google.maps.visualization.HeatmapLayer
    - Dedicated 'Google Maps' attribution line
    """
    import json
    import os

    resolved_key = (api_key or "").strip() or os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()

    landmark_images = {
        "Rajiv Chowk": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "Connaught Place": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "Kashmere Gate": "https://images.unsplash.com/photo-1597040663342-45b6af3d91a5?w=500&auto=format&fit=crop&q=80",
        "Seelampur": "https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=500&auto=format&fit=crop&q=80",
        "Anand Vihar": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=500&auto=format&fit=crop&q=80",
        "Jahangirpuri": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=500&auto=format&fit=crop&q=80",
        "Chandni Chowk": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=500&auto=format&fit=crop&q=80",
        "Karol Bagh": "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?w=500&auto=format&fit=crop&q=80",
        "Saket": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=500&auto=format&fit=crop&q=80",
        "India Gate": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80",
        "default": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=500&auto=format&fit=crop&q=80"
    }

    hotspot_records = []
    if hotspots_df is not None and not hotspots_df.empty:
        for _, r in hotspots_df.iterrows():
            d_name = str(r.get('district', 'Delhi'))
            p_name = str(r.get('dominant_premises', 'Hotspot'))
            img = landmark_images["default"]
            for k in landmark_images:
                if k.lower() in d_name.lower() or k.lower() in p_name.lower():
                    img = landmark_images[k]
                    break

            hotspot_records.append({
                "id": str(r.get("cluster_id", "")),
                "name": f"{d_name} - {p_name}",
                "district": d_name,
                "lat": float(r.get("centroid_lat", 28.6139)),
                "lon": float(r.get("centroid_lon", 77.2090)),
                "crime": str(r.get("primary_crime", "Street Crime")),
                "premises": p_name,
                "risk": float(r.get("avg_risk", 0.5)),
                "count": int(r.get("incident_count", 10)),
                "radius": float(r.get("radius_meters", 450)),
                "img": img
            })

    heatmap_points = []
    if incidents_df is not None and not incidents_df.empty:
        sample_df = incidents_df.sample(min(len(incidents_df), 1000), random_state=42)
        for _, r in sample_df.iterrows():
            try:
                lat = float(r.get("latitude", 0))
                lon = float(r.get("longitude", 0))
                if 28.30 <= lat <= 28.95 and 76.80 <= lon <= 77.50:
                    weight = 2.0 if bool(r.get("is_high_risk", False)) else 1.0
                    heatmap_points.append({"lat": lat, "lng": lon, "weight": weight})
            except Exception:
                continue

    hotspots_json = json.dumps(hotspot_records)
    heatmap_json = json.dumps(heatmap_points)

    center_lat = float(initial_user_lat) if initial_user_lat is not None else 28.6139
    center_lon = float(initial_user_lon) if initial_user_lon is not None else 77.2090
    user_present = "true" if initial_user_lat is not None else "false"
    init_zoom = int(initial_zoom) if initial_zoom else 13

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rakshak.ai Google Maps Sentinel Experience</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #030712;
      color: #f1f5f9;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }}
    .gmap-layout {{
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      background: #030712;
    }}
    /* Cruip Top Navigation Bar */
    .gmap-navbar {{
      flex-shrink: 0;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding: 10px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      z-index: 100;
    }}
    .gmap-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .gmap-logo {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      box-shadow: 0 2px 10px rgba(99, 102, 241, 0.4);
    }}
    .gmap-title {{
      font-weight: 800;
      font-size: 14px;
      color: #ffffff;
      letter-spacing: -0.02em;
    }}
    .gmap-badge {{
      font-size: 10px;
      font-family: 'Geist Mono', monospace;
      font-weight: 700;
      color: #818cf8;
      background: rgba(99, 102, 241, 0.15);
      padding: 2px 8px;
      border-radius: 9999px;
      border: 1px solid rgba(129, 140, 248, 0.3);
    }}
    /* Search Bar */
    .gmap-search-wrap {{
      flex: 1;
      max-width: 480px;
      position: relative;
    }}
    .gmap-search-input {{
      width: 100%;
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      padding: 8px 14px 8px 36px;
      color: #ffffff;
      font-size: 12.5px;
      outline: none;
      transition: all 0.2s ease;
    }}
    .gmap-search-input:focus {{
      border-color: rgba(99, 102, 241, 0.6);
      box-shadow: 0 0 16px rgba(99, 102, 241, 0.25);
      background: rgba(30, 41, 59, 0.95);
    }}
    .gmap-search-icon {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 13px;
      opacity: 0.6;
      pointer-events: none;
    }}
    /* Action Buttons */
    .gmap-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .gmap-btn {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .gmap-btn:hover, .gmap-btn.active {{
      background: rgba(99, 102, 241, 0.25);
      border-color: rgba(129, 140, 248, 0.5);
      color: #ffffff;
    }}
    /* Map Canvas */
    #map {{
      flex: 1;
      width: 100%;
      height: 100%;
      background: #030712;
    }}
    /* Key Prompt Modal */
    .gmap-modal-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(3, 7, 18, 0.88);
      backdrop-filter: blur(12px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 500;
      padding: 20px;
    }}
    .gmap-modal-card {{
      max-width: 520px;
      width: 100%;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid rgba(129, 140, 248, 0.35);
      border-radius: 20px;
      padding: 28px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.2);
      text-align: center;
    }}
    .gmap-modal-title {{
      font-size: 20px;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 8px;
    }}
    .gmap-modal-desc {{
      font-size: 13px;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 20px;
    }}
    .gmap-modal-input {{
      width: 100%;
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 10px;
      padding: 10px 14px;
      color: #ffffff;
      font-size: 13px;
      margin-bottom: 16px;
      outline: none;
      font-family: 'Geist Mono', monospace;
    }}
    .gmap-modal-btn {{
      background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 10px 24px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(79, 70, 229, 0.4);
      transition: all 0.2s ease;
    }}
    .gmap-modal-btn:hover {{
      background: linear-gradient(180deg, #4f46e5 0%, #4338ca 100%);
      transform: translateY(-1px);
    }}
    /* Attribution Footer */
    .gmap-footer {{
      flex-shrink: 0;
      background: rgba(15, 23, 42, 0.95);
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding: 6px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      color: #64748b;
      font-family: 'Geist Mono', monospace;
    }}
  </style>
</head>
<body>
  <div class="gmap-layout">
    <div class="gmap-navbar">
      <div class="gmap-brand">
        <div class="gmap-logo">🛡️</div>
        <div>
          <div class="gmap-title">Rakshak.ai Sentinel</div>
        </div>
        <span class="gmap-badge">Google Maps Platform</span>
      </div>

      <div class="gmap-search-wrap">
        <span class="gmap-search-icon">🔍</span>
        <input type="text" id="gmapSearch" class="gmap-search-input" placeholder="Search Delhi NCR address, metro station, or market..." />
      </div>

      <div class="gmap-actions">
        <button id="btnDark" class="gmap-btn active" onclick="setTheme('dark')">🌙 Night</button>
        <button id="btnHybrid" class="gmap-btn" onclick="setTheme('hybrid')">🛰️ Hybrid</button>
        <button id="btnTraffic" class="gmap-btn" onclick="toggleTraffic()">🚦 Traffic</button>
        <button id="btnHeatmap" class="gmap-btn active" onclick="toggleHeatmap()">🔥 Heatmap</button>
        <button id="btnGPS" class="gmap-btn" onclick="locateUser()">📍 Track GPS</button>
      </div>
    </div>

    <div style="position: relative; flex: 1; width: 100%; height: 100%;">
      <div id="map"></div>

      <div id="keyModal" class="gmap-modal-overlay" style="display: {'none' if resolved_key else 'flex'};">
        <div class="gmap-modal-card">
          <div style="font-size: 36px; margin-bottom: 12px;">🗺️</div>
          <div class="gmap-modal-title">Google Maps Platform Integration</div>
          <p class="gmap-modal-desc">
            Connect your Google Maps Platform API key to unlock hardware-accelerated Vector Maps, Live Traffic layers, 360° Street View, and Places Autocomplete for Delhi Crime Hotspots.
          </p>
          <input type="password" id="inputApiKey" class="gmap-modal-input" placeholder="AIzaSy..." value="{resolved_key}" />
          <button class="gmap-modal-btn" onclick="applyApiKey()">Launch Google Maps Sentinel</button>
          <div style="margin-top: 14px; font-size: 11px; color: #64748b;">
            Don't have a key? Get one on <a href="https://console.cloud.google.com/google/maps-apis/overview?utm_campaign=gmp_git_agentskills_v1" target="_blank" style="color: #818cf8; text-decoration: underline;">Google Cloud Console</a>.
          </div>
        </div>
      </div>
    </div>

    <div class="gmap-footer">
      <div>Sentinel Vector Engine • internalUsageAttributionIds: <code>gmp_git_agentskills_v1</code></div>
      <div>
        Google Maps
      </div>
    </div>
  </div>

  <script>
    const HOTSPOTS = {hotspots_json};
    const HEATMAP_DATA = {heatmap_json};
    const INITIAL_CENTER = {{ lat: {center_lat}, lng: {center_lon} }};
    const INITIAL_ZOOM = {init_zoom};
    const HAS_INITIAL_USER = {user_present};
    let ACTIVE_KEY = "{resolved_key}" || sessionStorage.getItem('gmp_api_key') || "";

    const NIGHT_STYLES = [
      {{ elementType: "geometry", stylers: [{{ color: "#0b0f19" }}] }},
      {{ elementType: "labels.text.stroke", stylers: [{{ color: "#0b0f19" }}] }},
      {{ elementType: "labels.text.fill", stylers: [{{ color: "#94a3b8" }}] }},
      {{ featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{{ color: "#e2e8f0" }}] }},
      {{ featureType: "poi", elementType: "labels.text.fill", stylers: [{{ color: "#94a3b8" }}] }},
      {{ featureType: "poi.park", elementType: "geometry", stylers: [{{ color: "#062024" }}] }},
      {{ featureType: "road", elementType: "geometry", stylers: [{{ color: "#1e293b" }}] }},
      {{ featureType: "road", elementType: "geometry.stroke", stylers: [{{ color: "#0f172a" }}] }},
      {{ featureType: "road.highway", elementType: "geometry", stylers: [{{ color: "#334155" }}] }},
      {{ featureType: "road.highway", elementType: "geometry.stroke", stylers: [{{ color: "#1e293b" }}] }},
      {{ featureType: "water", elementType: "geometry", stylers: [{{ color: "#031024" }}] }},
      {{ featureType: "water", elementType: "labels.text.fill", stylers: [{{ color: "#38bdf8" }}] }}
    ];

    let map = null;
    let trafficLayer = null;
    let heatmapLayer = null;
    let userMarker = null;
    let userCircle = null;
    let infoWindow = null;

    function applyApiKey() {{
      const k = document.getElementById('inputApiKey').value.trim();
      if (!k) return;
      ACTIVE_KEY = k;
      sessionStorage.setItem('gmp_api_key', k);
      document.getElementById('keyModal').style.display = 'none';
      loadGoogleMaps();
    }}

    function loadGoogleMaps() {{
      if (!ACTIVE_KEY) {{
        document.getElementById('keyModal').style.display = 'flex';
        return;
      }}
      document.getElementById('keyModal').style.display = 'none';

      // Official Dynamic Bootstrap Script Loader
      (g=>{{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={{}});var d=b.maps||(b.maps={{}}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${{c}}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))}})({{
        key: ACTIVE_KEY,
        v: "weekly"
      }});

      initSentinelMap();
    }}

    async function initSentinelMap() {{
      try {{
        const {{ Map }} = await google.maps.importLibrary("maps");
        const {{ AdvancedMarkerElement }} = await google.maps.importLibrary("marker").catch(() => ({{}}));
        const {{ HeatmapLayer }} = await google.maps.importLibrary("visualization").catch(() => ({{}}));
        const {{ Autocomplete }} = await google.maps.importLibrary("places").catch(() => ({{}}));

        // Initialize Map with mandatory usage attribution
        map = new Map(document.getElementById("map"), {{
          center: INITIAL_CENTER,
          zoom: INITIAL_ZOOM,
          styles: NIGHT_STYLES,
          mapTypeId: "roadmap",
          mapTypeControl: false,
          fullscreenControl: false,
          streetViewControl: true,
          // Mandatory tracking attribution ID
          internalUsageAttributionIds: ['gmp_git_agentskills_v1']
        }});

        infoWindow = new google.maps.InfoWindow();

        // Traffic Layer
        trafficLayer = new google.maps.TrafficLayer();

        // Heatmap Layer
        if (HeatmapLayer && HEATMAP_DATA.length > 0) {{
          const points = HEATMAP_DATA.map(p => ({{
            location: new google.maps.LatLng(p.lat, p.lng),
            weight: p.weight
          }}));
          heatmapLayer = new HeatmapLayer({{
            data: points,
            map: map,
            radius: 25,
            opacity: 0.75
          }});
        }}

        // Render Hotspot Corridors
        HOTSPOTS.forEach(h => {{
          const isHigh = h.risk >= 0.7;
          const strokeColor = isHigh ? "#ef4444" : "#f59e0b";
          const fillColor = isHigh ? "#dc2626" : "#d97706";

          // Circle overlay
          const circle = new google.maps.Circle({{
            strokeColor: strokeColor,
            strokeOpacity: 0.85,
            strokeWeight: 2,
            fillColor: fillColor,
            fillOpacity: 0.22,
            map: map,
            center: {{ lat: h.lat, lng: h.lon }},
            radius: h.radius || 500
          }});

          // Marker
          const marker = new google.maps.Marker({{
            position: {{ lat: h.lat, lng: h.lon }},
            map: map,
            title: h.name,
            icon: {{
              path: google.maps.SymbolPath.CIRCLE,
              scale: 7,
              fillColor: strokeColor,
              fillOpacity: 1,
              strokeColor: "#ffffff",
              strokeWeight: 2
            }}
          }});

          const contentString = `
            <div style="font-family: 'Inter', sans-serif; padding: 6px; max-width: 240px; color: #0f172a;">
              <img src="${{h.img}}" style="width: 100%; height: 90px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" />
              <div style="font-weight: 800; font-size: 13px; color: #0f172a;">${{h.name}}</div>
              <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Primary Crime: <b>${{h.crime}}</b></div>
              <div style="font-size: 11px; color: #64748b;">Incidents Logged: <b>${{h.count}}</b></div>
              <div style="margin-top: 6px; font-weight: 700; font-size: 11px; color: ${{isHigh ? '#dc2626' : '#d97706'}};">
                Risk Score: ${{(h.risk * 100).toFixed(0)}}% (${{isHigh ? 'HIGH DANGER' : 'MODERATE'}})
              </div>
            </div>
          `;

          marker.addListener("click", () => {{
            infoWindow.setContent(contentString);
            infoWindow.open(map, marker);
          }});

          circle.addListener("click", () => {{
            infoWindow.setContent(contentString);
            infoWindow.setPosition({{ lat: h.lat, lng: h.lon }});
            infoWindow.open(map);
          }});
        }});

        // Setup Autocomplete Search
        const searchInput = document.getElementById("gmapSearch");
        if (Autocomplete && searchInput) {{
          const autocomplete = new Autocomplete(searchInput, {{
            componentRestrictions: {{ country: "in" }},
            fields: ["geometry", "name", "formatted_address"]
          }});
          autocomplete.addListener("place_changed", () => {{
            const place = autocomplete.getPlace();
            if (place.geometry && place.geometry.location) {{
              map.setCenter(place.geometry.location);
              map.setZoom(15);
            }}
          }});
        }}

        // If user location is passed, show it
        if (HAS_INITIAL_USER) {{
          setUserPin(INITIAL_CENTER.lat, INITIAL_CENTER.lng);
        }}

      }} catch (err) {{
        console.error("Google Maps initialization failed:", err);
      }}
    }}

    function setUserPin(lat, lon) {{
      if (!map) return;
      const pos = new google.maps.LatLng(lat, lon);
      if (!userMarker) {{
        userMarker = new google.maps.Marker({{
          position: pos,
          map: map,
          title: "Your GPS Location",
          icon: {{
            path: google.maps.SymbolPath.CIRCLE,
            scale: 9,
            fillColor: "#38bdf8",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 3
          }}
        }});
        userCircle = new google.maps.Circle({{
          strokeColor: "#38bdf8",
          strokeOpacity: 0.5,
          strokeWeight: 1,
          fillColor: "#38bdf8",
          fillOpacity: 0.15,
          map: map,
          center: pos,
          radius: 300
        }});
      }} else {{
        userMarker.setPosition(pos);
        userCircle.setCenter(pos);
      }}
      map.panTo(pos);
    }}

    function locateUser() {{
      if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(pos => {{
        setUserPin(pos.coords.latitude, pos.coords.longitude);
        if (map) map.setZoom(15);
      }});
    }}

    function setTheme(t) {{
      if (!map) return;
      document.getElementById('btnDark').classList.remove('active');
      document.getElementById('btnHybrid').classList.remove('active');

      if (t === 'dark') {{
        document.getElementById('btnDark').classList.add('active');
        map.setMapTypeId("roadmap");
        map.setOptions({{ styles: NIGHT_STYLES }});
      }} else {{
        document.getElementById('btnHybrid').classList.add('active');
        map.setMapTypeId("hybrid");
        map.setOptions({{ styles: [] }});
      }}
    }}

    let isTrafficActive = false;
    function toggleTraffic() {{
      if (!trafficLayer || !map) return;
      isTrafficActive = !isTrafficActive;
      trafficLayer.setMap(isTrafficActive ? map : null);
      document.getElementById('btnTraffic').classList.toggle('active', isTrafficActive);
    }}

    let isHeatmapActive = true;
    function toggleHeatmap() {{
      if (!heatmapLayer) return;
      isHeatmapActive = !isHeatmapActive;
      heatmapLayer.setMap(isHeatmapActive ? map : null);
      document.getElementById('btnHeatmap').classList.toggle('active', isHeatmapActive);
    }}

    // Auto-init on load
    window.addEventListener("DOMContentLoaded", () => {{
      if (ACTIVE_KEY) {{
        loadGoogleMaps();
      }}
    }});
  </script>
</body>
</html>
"""
    return html_code
