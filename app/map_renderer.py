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
            <button id="btnSim" class="action-btn sim-btn" onclick="toggleSimulation()">🚀 Sim GPS</button>
            <button class="action-btn" onclick="centerOnMe()">📍 Me</button>
          </div>
          
        </header>
        
        <!-- Clean Map Canvas Viewport -->
        <main class="map-viewport">
          <div id="map"></div>
          
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
        
        function updateUserPosition(lat, lon, accuracy) {{
          currentUserPos = {{ lat, lon }};
          trailWaypoints.push([lat, lon]);
          trailPolyline.setLatLngs(trailWaypoints);
          
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
        
        let simTimer = null;
        let simIdx = 0;
        window.toggleSimulation = function() {{
          const btn = document.getElementById('btnSim');
          if (simTimer) {{
            clearInterval(simTimer);
            simTimer = null;
            btn.innerText = '🚀 Sim GPS';
            btn.classList.remove('active');
            return;
          }}
          
          btn.innerText = '⏹️ Stop Sim';
          btn.classList.add('active');
          simIdx = 0;
          const p0 = SIMULATION_ROUTE[0];
          updateUserPosition(p0.lat, p0.lon, 15);
          
          simTimer = setInterval(() => {{
            simIdx = (simIdx + 1) % SIMULATION_ROUTE.length;
            const p = SIMULATION_ROUTE[simIdx];
            updateUserPosition(p.lat, p.lon, 15);
          }}, 2800);
        }};
      </script>
    </body>
    </html>
    """
    return html_code

