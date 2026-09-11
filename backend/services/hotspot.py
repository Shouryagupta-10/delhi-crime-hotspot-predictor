"""
Rakshak.ai - Spatial Hotspot Detection Service
=============================================

This service implements spatial crime clustering using the Density-Based Spatial
Clustering of Applications with Noise (DBSCAN) algorithm from Scikit-Learn.

How DBSCAN Works for Geospatial Crime Detection:
------------------------------------------------
1. Density-Based Clustering:
   Unlike centroid-based clustering (such as K-Means), DBSCAN does not assume
   spherical clusters or require pre-specifying the number of clusters (k).
   It discovers arbitrary-shaped clusters based on local spatial density.

2. Key Parameters:
   - eps (Epsilon):
     The maximum geographical radius between two crime incidents for one to be
     considered in the neighborhood of the other.
     In this service, eps is supplied in kilometers (eps_km) and converted into
     radians for spherical distance calculations.
   - min_samples:
     The minimum number of crime incidents required within the eps neighborhood
     to identify a point as a 'core point' of a hotspot cluster. Higher values
     filter out incidental/sporadic crimes and retain only sustained crime clusters.

3. Geographical Distance Metric (Haversine Formula):
   Degrees of latitude and longitude cannot be treated as planar Euclidean coordinates.
   - Longitude degrees converge as distance from the equator increases. At Delhi's
     latitude (~28.6° N), 1° longitude ≈ 97.7 km, whereas 1° latitude ≈ 110.8 km.
     Using Cartesian Euclidean distance introduces substantial geographic distortion.
   - This service converts (latitude, longitude) coordinates to radians and utilizes
     the Haversine metric via a BallTree index, computing true great-circle spherical
     distances across the Earth's surface:
         distance = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1)*cos(lat2)*sin²(Δlon/2)))
     where Earth radius R ≈ 6371.0088 km.
   - Epsilon in radians = eps_km / 6371.0088.

4. Noise Point Classification:
   Points that do not meet the density threshold (fewer than min_samples neighbors
   within eps_km) are assigned cluster label -1 (Noise). In policing analytics,
   noise points represent isolated or opportunistic crimes that do not constitute
   a recurring hotspot.
"""

import time
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sklearn.cluster import DBSCAN

from models import CrimeRecord

# Earth's mean spherical radius in kilometers
EARTH_RADIUS_KM = 6371.0088


def detect_crime_hotspots(
    db: Session,
    eps_km: float = 0.5,
    min_samples: int = 25,
    district: Optional[str] = None,
    crime_type: Optional[str] = None,
    year: Optional[int] = None,
    min_severity: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Executes DBSCAN spatial clustering on crime records from SQLite.

    Parameters:
    -----------
    db : Session
        SQLAlchemy database session.
    eps_km : float
        Neighborhood radius in kilometers (default: 0.5 km = 500 meters).
    min_samples : int
        Minimum crime points required to form a dense hotspot cluster (default: 25).
    district : Optional[str]
        Optional filter by Delhi police district.
    crime_type : Optional[str]
        Optional filter by crime category.
    year : Optional[int]
        Optional filter by year.
    min_severity : Optional[int]
        Optional filter by minimum severity score (1-5).

    Returns:
    --------
    Dict containing detected hotspot clusters, noise statistics, and metadata.
    """
    start_time = time.time()

    # 1. Query spatial and attribute data from crime_records table
    query = db.query(
        CrimeRecord.crime_id,
        CrimeRecord.latitude,
        CrimeRecord.longitude,
        CrimeRecord.crime_type,
        CrimeRecord.district,
        CrimeRecord.severity_score
    )

    if district:
        query = query.filter(CrimeRecord.district.ilike(f"%{district}%"))
    if crime_type:
        query = query.filter(CrimeRecord.crime_type.ilike(f"%{crime_type}%"))
    if year:
        query = query.filter(CrimeRecord.year == year)
    if min_severity:
        query = query.filter(CrimeRecord.severity_score >= min_severity)

    results = query.all()
    total_points = len(results)

    if total_points == 0:
        return {
            "algorithm": "DBSCAN (Haversine Great-Circle Spatial Clustering)",
            "distance_metric_explanation": (
                "Coordinates are converted from degrees to radians and clustered using the "
                "Haversine metric with Earth radius 6371.0088 km to preserve accurate spatial distances."
            ),
            "parameters": {
                "eps_km": eps_km,
                "eps_radians": eps_km / EARTH_RADIUS_KM,
                "min_samples": min_samples,
                "distance_metric": "haversine"
            },
            "total_points_analyzed": 0,
            "total_clusters_detected": 0,
            "clustered_points_count": 0,
            "noise_points_count": 0,
            "noise_percentage": 0.0,
            "execution_time_seconds": round(time.time() - start_time, 4),
            "hotspots": []
        }

    # Convert query results to a DataFrame for vectorized operations
    df = pd.DataFrame([
        {
            "crime_id": r[0],
            "latitude": r[1],
            "longitude": r[2],
            "crime_type": r[3],
            "district": r[4],
            "severity_score": r[5]
        }
        for r in results
    ])

    # 2. Convert degrees to radians for Haversine metric
    coords_rad = np.radians(df[["latitude", "longitude"]].values)
    eps_rad = eps_km / EARTH_RADIUS_KM

    # 3. Fit DBSCAN using BallTree and Haversine metric
    # algorithm='ball_tree' is optimized for metric='haversine' on 2D coordinates
    dbscan = DBSCAN(
        eps=eps_rad,
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree"
    )
    cluster_labels = dbscan.fit_predict(coords_rad)
    df["cluster_id"] = cluster_labels

    # 4. Separate core/border cluster points from noise (-1)
    is_clustered = df["cluster_id"] != -1
    clustered_df = df[is_clustered]
    noise_df = df[~is_clustered]

    clustered_count = len(clustered_df)
    noise_count = len(noise_df)
    noise_percentage = round((noise_count / total_points) * 100, 2)

    # 5. Compute metrics for every detected hotspot cluster
    unique_clusters = sorted([c for c in np.unique(cluster_labels) if c != -1])
    total_clusters = len(unique_clusters)

    hotspots: List[Dict[str, Any]] = []

    for cid in unique_clusters:
        c_points = clustered_df[clustered_df["cluster_id"] == cid]
        count = len(c_points)

        # Center coordinates (mean centroid)
        center_lat = round(float(c_points["latitude"].mean()), 6)
        center_lon = round(float(c_points["longitude"].mean()), 6)

        # Percentages
        pct_of_clustered = round((count / clustered_count) * 100, 2) if clustered_count > 0 else 0.0
        pct_of_total = round((count / total_points) * 100, 2)

        # Primary administrative district in this hotspot
        primary_district = c_points["district"].mode().iloc[0] if not c_points["district"].empty else "Unknown"

        # Top 3 crime types in this cluster
        top_crimes = (
            c_points["crime_type"]
            .value_counts()
            .head(3)
            .reset_index()
            .rename(columns={"crime_type": "type", "count": "count"})
            .to_dict(orient="records")
        )

        # Average severity score
        avg_severity = round(float(c_points["severity_score"].mean()), 2)

        # Approximate cluster radius in meters (max distance from centroid)
        # Convert degrees to approximate meters (1 deg lat ≈ 111,000 m)
        d_lat_m = (c_points["latitude"] - center_lat) * 111000
        d_lon_m = (c_points["longitude"] - center_lon) * (111000 * np.cos(np.radians(center_lat)))
        radius_meters = round(float(np.sqrt(d_lat_m**2 + d_lon_m**2).max()), 1)

        hotspots.append({
            "cluster_id": int(cid),
            "crime_count": int(count),
            "center_latitude": center_lat,
            "center_longitude": center_lon,
            "percentage_of_clustered_crimes": pct_of_clustered,
            "percentage_of_total_crimes": pct_of_total,
            "primary_district": primary_district,
            "avg_severity": avg_severity,
            "radius_meters": radius_meters,
            "top_crime_types": top_crimes
        })

    # Sort hotspots by crime_count descending (most critical hotspots first)
    hotspots.sort(key=lambda x: x["crime_count"], reverse=True)

    execution_time = round(time.time() - start_time, 4)

    return {
        "algorithm": "DBSCAN (Density-Based Spatial Clustering of Applications with Noise)",
        "distance_metric_explanation": (
            "Geographical coordinates (lat, lon) are converted to radians and evaluated with the "
            f"Haversine formula on a sphere of radius {EARTH_RADIUS_KM} km. eps={eps_km} km corresponds "
            f"to {round(eps_rad, 7)} radians."
        ),
        "parameters": {
            "eps_km": eps_km,
            "eps_radians": round(eps_rad, 7),
            "min_samples": min_samples,
            "distance_metric": "haversine (BallTree)"
        },
        "total_points_analyzed": total_points,
        "total_clusters_detected": total_clusters,
        "clustered_points_count": clustered_count,
        "noise_points_count": noise_count,
        "noise_percentage": noise_percentage,
        "execution_time_seconds": execution_time,
        "hotspots": hotspots
    }
