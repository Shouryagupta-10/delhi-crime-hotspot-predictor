"""
Delhi Crime & Premises Dataset Generator
Generates realistic, grounded historical crime records across all 15 Delhi Police districts,
key police station jurisdictions, landmark premises, temporal profiles, and IPC crime types.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Fix seed for reproducible, high-quality benchmark data
np.random.seed(42)
random.seed(42)

DISTRICTS = {
    "New Delhi": {
        "center": (28.6139, 77.2090),
        "police_stations": ["Connaught Place", "Chanakyapuri", "Parliament Street", "Mandir Marg", "Tilak Marg"],
        "landmarks": [
            ("Connaught Place Inner Circle", "Commercial & Retail Market", 28.6315, 77.2167, 1.2),
            ("Rajiv Chowk Metro Interchange", "Transit & Metro Hub", 28.6328, 77.2195, 1.4),
            ("Khan Market", "Commercial & Retail Market", 28.6003, 77.2270, 0.6),
            ("Chanakyapuri Diplomatic Enclave", "Residential Gated Colony", 28.5921, 77.1856, 0.3),
            ("Barakhamba Road ATM Cluster", "Bank & ATM Premises", 28.6290, 77.2240, 0.8),
        ]
    },
    "Central": {
        "center": (28.6448, 77.2167),
        "police_stations": ["Karol Bagh", "Paharganj", "Daryaganj", "Chandni Chowk", "Rajinder Nagar"],
        "landmarks": [
            ("Karol Bagh Gaffar Market", "Commercial & Retail Market", 28.6517, 77.1906, 1.5),
            ("Paharganj Hotel & Station Corridor", "Transit & Metro Hub", 28.6432, 77.2140, 1.6),
            ("Daryaganj Sunday Book Market Area", "Street & Public Roadways", 28.6480, 77.2410, 1.1),
            ("Chandni Chowk Main Street", "Commercial & Retail Market", 28.6562, 77.2300, 1.4),
            ("New Delhi Railway Station Gate 2", "Transit & Metro Hub", 28.6420, 77.2210, 1.7),
        ]
    },
    "North": {
        "center": (28.6800, 77.2100),
        "police_stations": ["Kashmere Gate", "Civil Lines", "Timarpur", "Sadar Bazar", "Maurice Nagar"],
        "landmarks": [
            ("Kashmere Gate ISBT & Metro", "Transit & Metro Hub", 28.6675, 77.2285, 1.8),
            ("Delhi University North Campus Arts Faculty", "Educational & Campus Environs", 28.6890, 77.2080, 0.9),
            ("Sadar Bazar Wholesale Market", "Commercial & Retail Market", 28.6550, 77.2100, 1.4),
            ("Civil Lines Rajpur Road", "Residential Gated Colony", 28.6750, 77.2230, 0.5),
            ("Kamla Nagar Market", "Commercial & Retail Market", 28.6815, 77.2025, 1.2),
        ]
    },
    "South": {
        "center": (28.5400, 77.2000),
        "police_stations": ["Hauz Khas", "Saket", "Malviya Nagar", "Mehrauli", "Greater Kailash"],
        "landmarks": [
            ("Hauz Khas Village Social Hub", "Commercial & Retail Market", 28.5535, 77.1945, 1.3),
            ("Saket Select Citywalk Environs", "Commercial & Retail Market", 28.5285, 77.2185, 1.1),
            ("Malviya Nagar Shivalik Colony", "Residential Gated Colony", 28.5360, 77.2090, 0.7),
            ("Mehrauli Archaeological Park Perimeter", "Parks & Isolated Environs", 28.5240, 77.1850, 1.4),
            ("Hauz Khas Metro Station Interchange", "Transit & Metro Hub", 28.5430, 77.2060, 1.2),
        ]
    },
    "South-East": {
        "center": (28.5600, 77.2500),
        "police_stations": ["Lajpat Nagar", "Nehru Place", "Kalkaji", "Sarita Vihar", "Okhla"],
        "landmarks": [
            ("Nehru Place IT & Electronics Complex", "Commercial & Retail Market", 28.5494, 77.2528, 1.5),
            ("Lajpat Nagar Central Market", "Commercial & Retail Market", 28.5677, 77.2433, 1.4),
            ("Okhla Phase 3 Industrial Estate", "Industrial & Warehouse Estates", 28.5350, 77.2720, 1.3),
            ("Kalkaji Mandir Metro Hub", "Transit & Metro Hub", 28.5490, 77.2580, 1.2),
            ("Greater Kailash 1 M-Block Market", "Commercial & Retail Market", 28.5540, 77.2340, 0.8),
        ]
    },
    "South-West": {
        "center": (28.5600, 77.1500),
        "police_stations": ["Vasant Kunj", "Vasant Vihar", "Delhi Cantt", "RK Puram", "Mahipalpur"],
        "landmarks": [
            ("Mahipalpur Highway Hotel Corridor", "Street & Public Roadways", 28.5430, 77.1260, 1.5),
            ("Vasant Kunj Promenade Mall", "Commercial & Retail Market", 28.5420, 77.1560, 0.9),
            ("RK Puram Sector 4 Complex", "Residential Gated Colony", 28.5680, 77.1820, 0.6),
            ("Dhaula Kuan Underpass Intersection", "Street & Public Roadways", 28.5925, 77.1610, 1.4),
            ("Vasant Vihar Basant Lok Market", "Commercial & Retail Market", 28.5580, 77.1620, 0.7),
        ]
    },
    "West": {
        "center": (28.6500, 77.1200),
        "police_stations": ["Rajouri Garden", "Punjabi Bagh", "Janakpuri", "Tilak Nagar", "Patel Nagar"],
        "landmarks": [
            ("Rajouri Garden Main Market", "Commercial & Retail Market", 28.6490, 77.1230, 1.3),
            ("Janakpuri District Centre", "Commercial & Retail Market", 28.6290, 77.0810, 1.2),
            ("Punjabi Bagh Club Road", "Street & Public Roadways", 28.6680, 77.1270, 1.1),
            ("Tilak Nagar Metro Station", "Transit & Metro Hub", 28.6365, 77.0965, 1.3),
            ("Mayapuri Industrial Area Phase 2", "Industrial & Warehouse Estates", 28.6350, 77.1350, 1.4),
        ]
    },
    "North-West": {
        "center": (28.7000, 77.1500),
        "police_stations": ["Netaji Subhash Place", "Model Town", "Shalimar Bagh", "Ashok Vihar", "Bharat Nagar"],
        "landmarks": [
            ("Netaji Subhash Place Commercial Hub", "Commercial & Retail Market", 28.6925, 77.1520, 1.3),
            ("Model Town 2 Gujranwala Town", "Residential Gated Colony", 28.7050, 77.1920, 0.7),
            ("Shalimar Bagh Club Road", "Street & Public Roadways", 28.7150, 77.1600, 0.8),
            ("Ashok Vihar Deep Market", "Commercial & Retail Market", 28.6880, 77.1750, 0.9),
            ("Wazirpur Industrial Area", "Industrial & Warehouse Estates", 28.6980, 77.1680, 1.4),
        ]
    },
    "Rohini": {
        "center": (28.7300, 77.1000),
        "police_stations": ["Rohini Sector 18", "Prashant Vihar", "South Rohini", "Begumpur", "Kanjhawala"],
        "landmarks": [
            ("Rohini Sector 18 Metro & DDA Market", "Transit & Metro Hub", 28.7410, 77.1320, 1.4),
            ("Prashant Vihar Institutional Area", "Bank & ATM Premises", 28.7110, 77.1350, 1.1),
            ("Rohini Sector 3 Japanese Park Perimeter", "Parks & Isolated Environs", 28.7180, 77.1180, 1.3),
            ("Rithala Metro Terminal", "Transit & Metro Hub", 28.7205, 77.1070, 1.5),
            ("Begumpur Main Chowk", "Street & Public Roadways", 28.7290, 77.0780, 1.2),
        ]
    },
    "Dwarka": {
        "center": (28.5800, 77.0500),
        "police_stations": ["Dwarka Sector 10", "Dwarka Sector 23", "Dwarka North", "Dwarka South", "Uttam Nagar"],
        "landmarks": [
            ("Dwarka Sector 10 District Court & Market", "Commercial & Retail Market", 28.5810, 77.0580, 1.1),
            ("Dwarka Sector 21 Metro Interchange", "Transit & Metro Hub", 28.5520, 77.0580, 1.3),
            ("Uttam Nagar East Metro Chowk", "Transit & Metro Hub", 28.6210, 77.0650, 1.7),
            ("Dwarka Sector 6 Commercial Pocket", "Commercial & Retail Market", 28.5910, 77.0670, 0.9),
            ("Najafgarh Road Trunk Highway", "Street & Public Roadways", 28.6180, 77.0300, 1.4),
        ]
    },
    "East": {
        "center": (28.6200, 77.2900),
        "police_stations": ["Laxmi Nagar", "Preet Vihar", "Mayur Vihar 1", "Kalyanpuri", "Pandav Nagar"],
        "landmarks": [
            ("Laxmi Nagar Vikas Marg Market", "Commercial & Retail Market", 28.6310, 77.2780, 1.5),
            ("Preet Vihar Commercial Complex", "Commercial & Retail Market", 28.6410, 77.2950, 0.9),
            ("Mayur Vihar Phase 1 Pocket 1", "Residential Gated Colony", 28.6080, 77.2950, 0.6),
            ("Akshardham Metro Station Corridor", "Transit & Metro Hub", 28.6180, 77.2790, 1.2),
            ("Kalyanpuri Bus Terminal Environs", "Transit & Metro Hub", 28.6190, 77.3150, 1.4),
        ]
    },
    "Shahdara": {
        "center": (28.6700, 77.2900),
        "police_stations": ["Anand Vihar", "Vivek Vihar", "Gandhi Nagar", "Krishna Nagar", "Farsh Bazar"],
        "landmarks": [
            ("Anand Vihar ISBT & Railway Terminal", "Transit & Metro Hub", 28.6480, 77.3160, 1.9),
            ("Gandhi Nagar Textile Wholesale Market", "Commercial & Retail Market", 28.6610, 77.2680, 1.5),
            ("Krishna Nagar Lal Quarter Market", "Commercial & Retail Market", 28.6590, 77.2840, 1.3),
            ("Vivek Vihar Block B", "Residential Gated Colony", 28.6710, 77.3120, 0.7),
            ("Shahdara Railway Station Chauraha", "Transit & Metro Hub", 28.6740, 77.2900, 1.4),
        ]
    },
    "North-East": {
        "center": (28.7000, 77.2700),
        "police_stations": ["Seelampur", "Bhajanpura", "Gokulpuri", "Khajuri Khas", "Jafrabad"],
        "landmarks": [
            ("Seelampur Metro & Market Chowk", "Transit & Metro Hub", 28.6690, 77.2670, 1.7),
            ("Bhajanpura Wazirabad Road Intersection", "Street & Public Roadways", 28.7010, 77.2630, 1.5),
            ("Gokulpuri Tyre Market", "Commercial & Retail Market", 28.7030, 77.2810, 1.3),
            ("Khajuri Khas Flyover Junction", "Street & Public Roadways", 28.7180, 77.2550, 1.4),
            ("Jafrabad Main Road", "Street & Public Roadways", 28.6820, 77.2690, 1.6),
        ]
    },
    "Outer": {
        "center": (28.6900, 77.0500),
        "police_stations": ["Mangolpuri", "Sultanpuri", "Nangloi", "Paschim Vihar", "Mianwali Nagar"],
        "landmarks": [
            ("Mangolpuri Industrial Area Phase 1", "Industrial & Warehouse Estates", 28.6910, 77.0860, 1.6),
            ("Nangloi Metro Rohtak Road", "Transit & Metro Hub", 28.6830, 77.0650, 1.5),
            ("Sultanpuri C-Block Market", "Commercial & Retail Market", 28.7050, 77.0780, 1.4),
            ("Paschim Vihar Jwala Heri Market", "Commercial & Retail Market", 28.6730, 77.1080, 1.0),
            ("Peeragarhi Intersection & Metro", "Transit & Metro Hub", 28.6790, 77.0940, 1.6),
        ]
    },
    "Outer-North": {
        "center": (28.7800, 77.1200),
        "police_stations": ["Narela", "Bawana", "Samaypur Badli", "Alipur", "Shahbad Daulatpur"],
        "landmarks": [
            ("Bawana Industrial Estate Sector 3", "Industrial & Warehouse Estates", 28.7980, 77.0420, 1.7),
            ("Narela Food Park & Mandi", "Commercial & Retail Market", 28.8450, 77.0920, 1.4),
            ("Samaypur Badli Metro & Railway Hub", "Transit & Metro Hub", 28.7460, 77.1420, 1.5),
            ("GT Karnal Road Singhu Border Stretch", "Street & Public Roadways", 28.8780, 77.1260, 1.3),
            ("Shahbad Dairy Area", "Residential Gated Colony", 28.7560, 77.1120, 1.4),
        ]
    }
}

CRIME_TYPES = {
    "Snatching (Chain/Mobile)": {
        "severity": 3,
        "ipc": "IPC 379/356 (BNS 304)",
        "peak_hours": [17, 18, 19, 20, 21, 22],
        "favored_premises": ["Street & Public Roadways", "Commercial & Retail Market", "Transit & Metro Hub"],
        "weight": 0.26
    },
    "Motor Vehicle Theft": {
        "severity": 3,
        "ipc": "IPC 379 (BNS 303)",
        "peak_hours": [22, 23, 0, 1, 2, 3, 4],
        "favored_premises": ["Residential Gated Colony", "Street & Public Roadways", "Transit & Metro Hub"],
        "weight": 0.28
    },
    "Burglary & House Breaking": {
        "severity": 4,
        "ipc": "IPC 380/457 (BNS 305/331)",
        "peak_hours": [1, 2, 3, 4, 13, 14],
        "favored_premises": ["Residential Gated Colony", "Commercial & Retail Market", "Industrial & Warehouse Estates"],
        "weight": 0.16
    },
    "Street Robbery / Mugging": {
        "severity": 4,
        "ipc": "IPC 392/394 (BNS 309)",
        "peak_hours": [20, 21, 22, 23, 0, 1],
        "favored_premises": ["Street & Public Roadways", "Transit & Metro Hub", "Parks & Isolated Environs"],
        "weight": 0.14
    },
    "Pickpocketing & Luggage Theft": {
        "severity": 2,
        "ipc": "IPC 379 (BNS 303)",
        "peak_hours": [8, 9, 10, 16, 17, 18, 19],
        "favored_premises": ["Transit & Metro Hub", "Commercial & Retail Market"],
        "weight": 0.10
    },
    "Assault & Public Brawl": {
        "severity": 3,
        "ipc": "IPC 323/341 (BNS 115/126)",
        "peak_hours": [21, 22, 23, 0],
        "favored_premises": ["Commercial & Retail Market", "Street & Public Roadways"],
        "weight": 0.06
    }
}

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

try:
    from .cleaner import clean_crime_dataset
except (ImportError, ValueError):
    from cleaner import clean_crime_dataset

def generate_delhi_crime_dataset(num_records=35000, output_path=None, raw_output_path=None, inject_noise=True, start_year=2015):
    """
    Generates realistic raw Delhi police incident reports spanning past 10 years (from 2015
    to recent date) with confirmation statuses, temporal dynamics, and geocodes. Applies
    rigorous data cleaning to ensure that downstream hotspot maps and predictive models run
    exclusively on confirmed, fully populated (no missing data) records.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if output_path is None:
        output_path = os.path.join(base_dir, "delhi_crime_records.csv")
    if raw_output_path is None:
        raw_output_path = os.path.join(base_dir, "raw_delhi_police_reports.csv")

    records = []
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    total_days = max(1, (end_date - start_date).days)
    
    crime_names = list(CRIME_TYPES.keys())
    crime_weights = [CRIME_TYPES[c]["weight"] for c in crime_names]
    district_names = list(DISTRICTS.keys())
    
    # Confirmation statuses and distribution
    status_choices = ["Confirmed", "Pending Investigation", "Unconfirmed / Unverified Tip", "False Alarm / Dismissed"]
    status_weights = [0.80, 0.11, 0.05, 0.04]
    
    for i in range(num_records):
        dist_name = random.choice(district_names)
        dist_info = DISTRICTS[dist_name]
        
        landmark_name, premises_type, lat_c, lon_c, density_multiplier = random.choice(dist_info["landmarks"])
        ps_name = random.choice(dist_info["police_stations"])
        
        crime_type = random.choices(crime_names, weights=crime_weights, k=1)[0]
        c_meta = CRIME_TYPES[crime_type]
        
        if random.random() < 0.65:
            hour = random.choice(c_meta["peak_hours"])
        else:
            hour = random.randint(0, 23)
            
        minute = random.randint(0, 59)
        day_offset = random.randint(0, total_days)
        dt = start_date + timedelta(days=day_offset, hours=hour, minutes=minute)
        incident_year = dt.year
        day_name = dt.strftime("%A")
        is_weekend = 1 if day_name in ["Saturday", "Sunday"] else 0
        
        # Jitter coordinates
        jitter_std = 0.0028 / density_multiplier
        lat = round(float(np.random.normal(lat_c, jitter_std)), 6)
        lon = round(float(np.random.normal(lon_c, jitter_std)), 6)
        
        lat = max(28.40, min(28.90, lat))
        lon = max(76.85, min(77.40, lon))
        
        base_severity = c_meta["severity"]
        is_night = 1 if (hour >= 22 or hour <= 5) else 0
        is_rush_hour = 1 if (hour in [8, 9, 10, 17, 18, 19, 20]) else 0
        
        premises_risk_score = 0.5
        if premises_type in ["Transit & Metro Hub", "Commercial & Retail Market"]:
            premises_risk_score += 0.25
        elif premises_type in ["Parks & Isolated Environs", "Industrial & Warehouse Estates"]:
            premises_risk_score += 0.20 if is_night else 0.05
            
        risk_metric = (base_severity / 5.0) * 0.4 + (premises_risk_score * 0.35) + (is_night * 0.15) + (is_weekend * 0.10)
        risk_metric = min(1.0, max(0.0, risk_metric + np.random.normal(0, 0.05)))
        
        if risk_metric >= 0.65:
            risk_level = "High"
        elif risk_metric >= 0.42:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        # Confirmation status
        status = random.choices(status_choices, weights=status_weights, k=1)[0]
        
        rec = {
            "record_id": f"DEL-FIR-{incident_year}-{100000 + i}",
            "year": incident_year,
            "district": dist_name,
            "police_station": ps_name,
            "landmark_premise": landmark_name,
            "premises_type": premises_type,
            "crime_category": crime_type,
            "statutory_ipc": c_meta["ipc"],
            "date": dt.strftime("%Y-%m-%d"),
            "hour": hour,
            "minute": minute,
            "day_of_week": day_name,
            "is_weekend": is_weekend,
            "is_night": is_night,
            "is_rush_hour": is_rush_hour,
            "latitude": lat,
            "longitude": lon,
            "severity_score": base_severity,
            "risk_index": round(float(risk_metric), 3),
            "risk_level": risk_level,
            "is_high_risk": 1 if risk_level == "High" else 0,
            "confirmation_status": status
        }
        
        # Inject realistic noise & missing data into raw logs
        if inject_noise:
            rand_flag = random.random()
            if rand_flag < 0.035:
                # Missing coordinates
                rec["latitude"] = np.nan
                rec["longitude"] = np.nan
            elif rand_flag < 0.050:
                # Out-of-bounds coordinates (outside Delhi NCT)
                rec["latitude"] = round(float(random.uniform(29.60, 31.00)), 6)
                rec["longitude"] = round(float(random.uniform(75.00, 76.50)), 6)
            elif rand_flag < 0.065:
                # Missing critical attributes
                if random.random() < 0.5:
                    rec["district"] = np.nan
                else:
                    rec["crime_category"] = np.nan
            elif rand_flag < 0.075:
                # Invalid temporal values
                rec["hour"] = 99
                
        records.append(rec)
        
    # Inject ~1.5% duplicate incident records to simulate multi-source duplicate filing
    if inject_noise and len(records) > 100:
        num_dups = int(num_records * 0.015)
        for _ in range(num_dups):
            dup_idx = random.randint(0, len(records) - 1)
            records.append(dict(records[dup_idx]))
        
    raw_df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(raw_output_path), exist_ok=True)
    raw_df.to_csv(raw_output_path, index=False)
    print(f"Generated {len(raw_df)} raw Delhi police reports at {raw_output_path}")
    print("Raw Confirmation Status Breakdown:")
    print(raw_df["confirmation_status"].value_counts(normalize=True))
    
    # Execute production data cleaning pipeline
    clean_df, audit = clean_crime_dataset(raw_df)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_df.to_csv(output_path, index=False)
    
    # Also sync to backend/data if present
    backend_data_dir = os.path.join(os.path.dirname(base_dir), "backend", "data")
    if os.path.exists(backend_data_dir):
        try:
            import shutil
            shutil.copy(raw_output_path, os.path.join(backend_data_dir, os.path.basename(raw_output_path)))
            shutil.copy(output_path, os.path.join(backend_data_dir, os.path.basename(output_path)))
        except Exception as e:
            print(f"Note: Could not sync to backend/data: {e}")

    print(f"\n✅ Data Cleaning Pipeline Completed Successfully:")
    print(f"   Raw Ingestion:        {audit['raw_count']} records")
    print(f"   Unconfirmed Dropped:  {audit['unconfirmed_dropped']}")
    print(f"   Missing GPS Dropped:  {audit['missing_coords_dropped']}")
    print(f"   Missing Cols Dropped: {audit['missing_critical_fields_dropped']}")
    print(f"   Out-of-Bounds Dropped:{audit['out_of_bounds_coords_dropped']}")
    print(f"   Duplicates Dropped:   {audit['duplicates_dropped']}")
    print(f"   Cleaned & Verified:   {audit['cleaned_count']} records ({audit['retention_rate_pct']}% retention)")
    print(f"   Clean Dataset saved at {output_path}")
    return clean_df

if __name__ == "__main__":
    generate_delhi_crime_dataset()
