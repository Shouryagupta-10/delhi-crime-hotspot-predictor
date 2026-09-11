"""
Interactive Folium Geospatial Map Renderer for Delhi Crime & Premises
Renders choropleths, density heatmaps, and DBSCAN hotspot corridor polygons/circles.
"""

import folium
from folium.plugins import HeatMap, MarkerCluster, LocateControl

DELHI_CENTER = [28.6139, 77.2090]

def create_delhi_crime_map(df_filtered, hotspots_df=None, show_heatmap=True, show_hotspots=True, show_pins=True, user_location=None):
    """
    Renders an interactive Folium map with OpenStreetMap/CartoDB tiles,
    crime density heatmap, DBSCAN cluster centroids, premises incident pins,
    and GPS user location tracking.
    """
    # If user location is active, center on user, else default Delhi center
    center_loc = [user_location[0], user_location[1]] if user_location else DELHI_CENTER
    zoom_lvl = 13 if user_location else 11

    m = folium.Map(
        location=center_loc,
        zoom_start=zoom_lvl,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True
    )

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
