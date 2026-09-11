"""
Multi-City & Open Data Ingestion Engine
Enables seamless ingestion of diverse civic and municipal crime datasets
(e.g., Delhi Police, India NCRB/State Police portal, Chicago Open Data, LA Crime Data)
with dynamic schema mapping, spatial geofencing, and validation.
Fulfills Build with Bharat 2.0 Slide 6: Multi-City Scalability with Zero Architectural Changes.
"""

import os
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

CITY_REGISTRY = {
    "Delhi NCT": {
        "lat_bounds": (28.30, 28.95),
        "lon_bounds": (76.80, 77.50),
        "center": (28.6139, 77.2090),
        "districts": [
            "New Delhi", "Central", "North", "South", "South-East", "South-West",
            "West", "North-West", "Rohini", "Dwarka", "East", "Shahdara",
            "North-East", "Outer", "Outer-North"
        ]
    },
    "Chicago (Open Portal)": {
        "lat_bounds": (41.60, 42.05),
        "lon_bounds": (-87.95, -87.50),
        "center": (41.8781, -87.6298),
        "districts": ["District 1", "District 2", "District 12", "District 18", "District 19"]
    },
    "Mumbai (NCRB Format)": {
        "lat_bounds": (18.88, 19.30),
        "lon_bounds": (72.75, 73.05),
        "center": (19.0760, 72.8777),
        "districts": ["South Mumbai", "Central Mumbai", "Western Suburbs", "Eastern Suburbs"]
    },
    "Bengaluru": {
        "lat_bounds": (12.80, 13.15),
        "lon_bounds": (77.45, 77.78),
        "center": (12.9716, 77.5946),
        "districts": ["East", "West", "North", "South", "Central"]
    }
}

# Universal column mappings from open data formats to Rakshak.ai schema
SCHEMA_MAPPINGS = {
    "chicago_open_data": {
        "Case Number": "record_id",
        "Primary Type": "crime_category",
        "Location Description": "premises_type",
        "District": "district",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Date": "date_raw"
    },
    "ncrb_india_format": {
        "FIR_NO": "record_id",
        "OFFENCE_HEAD": "crime_category",
        "PLACE_OF_OCCURRENCE": "landmark_premise",
        "DISTRICT": "district",
        "POLICE_STATION": "police_station",
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "DATE_OF_OCCURRENCE": "date_raw",
        "CONFIRMATION": "confirmation_status"
    }
}

class MultiCityIngestionEngine:
    """
    Ingests, standardizes, and validates heterogeneous crime datasets
    across metropolitan jurisdictions worldwide.
    """

    def __init__(self, city_name: str = "Delhi NCT"):
        if city_name not in CITY_REGISTRY:
            raise ValueError(f"Unsupported city '{city_name}'. Supported: {list(CITY_REGISTRY.keys())}")
        self.city_name = city_name
        self.city_meta = CITY_REGISTRY[city_name]

    def standardize_schema(self, raw_df: pd.DataFrame, schema_preset: Optional[str] = None) -> pd.DataFrame:
        """Harmonizes arbitrary column names into Rakshak.ai unified format."""
        df = raw_df.copy()
        
        # 1. Apply explicit preset if supplied
        if schema_preset and schema_preset in SCHEMA_MAPPINGS:
            mapping = SCHEMA_MAPPINGS[schema_preset]
            df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
            
        # 2. Automated fuzzy heuristic column aliasing
        alias_dict = {
            "lat": "latitude",
            "latitude": "latitude",
            "latitude_deg": "latitude",
            "lon": "longitude",
            "longitude": "longitude",
            "lng": "longitude",
            "longitude_deg": "longitude",
            "crime": "crime_category",
            "primary_type": "crime_category",
            "offense": "crime_category",
            "offence": "crime_category",
            "incident_type": "crime_category",
            "premise": "premises_type",
            "premises": "premises_type",
            "location_description": "premises_type",
            "district": "district",
            "station": "police_station",
            "id": "record_id",
            "fir_number": "record_id",
            "case_number": "record_id"
        }
        
        rename_map = {}
        for col in df.columns:
            cleaned_col = str(col).lower().strip().replace(" ", "_")
            if cleaned_col in alias_dict:
                target = alias_dict[cleaned_col]
                if col != target and target not in df.columns:
                    rename_map[col] = target
        df = df.rename(columns=rename_map)

        # 3. Handle timestamps
        if "date_raw" in df.columns and "date" not in df.columns:
            try:
                parsed_dt = pd.to_datetime(df["date_raw"], errors="coerce")
                df["date"] = parsed_dt.dt.strftime("%Y-%m-%d")
                if "hour" not in df.columns:
                    df["hour"] = parsed_dt.dt.hour.fillna(12).astype(int)
                if "day_of_week" not in df.columns:
                    df["day_of_week"] = parsed_dt.dt.day_name().fillna("Monday")
            except Exception:
                pass

        return df

    def validate_and_geofence(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Filters coordinates against target city geofence and drops missing essentials."""
        std_df = self.standardize_schema(df)
        raw_count = len(std_df)

        # Ensure numeric lat/lon
        for c in ["latitude", "longitude"]:
            if c in std_df.columns:
                std_df[c] = pd.to_numeric(std_df[c], errors="coerce")

        std_df = std_df.dropna(subset=["latitude", "longitude"])
        
        # Spatial Geofence
        lat_min, lat_max = self.city_meta["lat_bounds"]
        lon_min, lon_max = self.city_meta["lon_bounds"]
        
        bounded = std_df[
            (std_df["latitude"] >= lat_min) & (std_df["latitude"] <= lat_max) &
            (std_df["longitude"] >= lon_min) & (std_df["longitude"] <= lon_max)
        ].copy()

        # Defaults for missing auxiliary attributes
        if "district" not in bounded.columns:
            bounded["district"] = self.city_meta["districts"][0]
        if "premises_type" not in bounded.columns:
            bounded["premises_type"] = "Street & Public Roadways"
        if "crime_category" not in bounded.columns:
            bounded["crime_category"] = "Theft / Property Crime"
        if "hour" not in bounded.columns:
            bounded["hour"] = 18
        if "day_of_week" not in bounded.columns:
            bounded["day_of_week"] = "Friday"
        if "is_weekend" not in bounded.columns:
            bounded["is_weekend"] = bounded["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
        if "is_night" not in bounded.columns:
            bounded["is_night"] = bounded["hour"].apply(lambda h: 1 if (h >= 22 or h <= 5) else 0)
        if "is_rush_hour" not in bounded.columns:
            bounded["is_rush_hour"] = bounded["hour"].apply(lambda h: 1 if h in [8, 9, 10, 17, 18, 19, 20] else 0)
        if "severity_score" not in bounded.columns:
            bounded["severity_score"] = 3

        bounded["city"] = self.city_name
        cleaned_count = len(bounded)

        audit = {
            "target_city": self.city_name,
            "raw_input_rows": raw_count,
            "geofenced_rows": cleaned_count,
            "out_of_bounds_dropped": raw_count - cleaned_count,
            "retention_rate": round((cleaned_count / raw_count * 100) if raw_count > 0 else 0, 2)
        }
        return bounded.reset_index(drop=True), audit

def generate_sample_external_dataset(city: str = "Chicago (Open Portal)", num_rows: int = 200) -> pd.DataFrame:
    """Generates synthetic external open data formatted records to test multi-city portability."""
    meta = CITY_REGISTRY.get(city, CITY_REGISTRY["Chicago (Open Portal)"])
    c_lat, c_lon = meta["center"]
    records = []
    for i in range(num_rows):
        lat = round(float(np.random.normal(c_lat, 0.04)), 5)
        lon = round(float(np.random.normal(c_lon, 0.04)), 5)
        records.append({
            "Case Number": f"EXT-CASE-{2025}-{20000+i}",
            "Primary Type": np.random.choice(["ROBBERY", "MOTOR VEHICLE THEFT", "BATTERY", "BURGLARY"]),
            "Location Description": np.random.choice(["STREET", "SIDEWALK", "RESIDENCE", "GAS STATION"]),
            "District": np.random.choice(meta["districts"]),
            "Latitude": lat,
            "Longitude": lon,
            "Date": "2025-06-15 22:30:00"
        })
    return pd.DataFrame(records)
