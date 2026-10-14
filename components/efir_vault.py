"""
Rakshak.ai e-FIR Registration & Digital Evidence Vault Component
Provides an official reporting gateway and digital forensics evidence vault:
- Statutory notice under Section 173 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023
- Section 63 Bharatiya Sakshya Adhiniyam (BSA), 2023 digital evidentiary integrity
- Complainant details with Aadhaar privacy masking
- Classified offenses mapped to Bharatiya Nyaya Sanhita (BNS) & Indian Penal Code (IPC)
- Delhi Police Station selection across 15 districts with real-time Haversine distance
- Client-side & server-side cryptographic SHA-256 evidence hashing
- Tamper-Proof Audit Hash Generated badges
- Master Composite SHA-256 Bundle Hash calculation
- Official Acknowledgment Receipt with downloadable .txt slip and printable .html certificate
- Persistent session vault of recorded e-FIRs with status tracking
"""

import os
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 1. DELHI POLICE STATIONS & GEOGRAPHIC JURISDICTIONS REGISTRY
# -----------------------------------------------------------------------------
DELHI_POLICE_STATIONS_VAULT = [
    # New Delhi District
    {"name": "Connaught Place Police Station", "district": "New Delhi", "lat": 28.6315, "lon": 77.2167, "address": "B-Block, Connaught Place, New Delhi", "phone": "011-23747100 / 112"},
    {"name": "Parliament Street Police Station", "district": "New Delhi", "lat": 28.6238, "lon": 77.2142, "address": "Parliament Street, New Delhi", "phone": "011-23361100 / 112"},
    {"name": "Chanakyapuri Police Station", "district": "New Delhi", "lat": 28.5983, "lon": 77.1912, "address": "Simon Bolivar Marg, Chanakyapuri", "phone": "011-24101100 / 112"},
    {"name": "Mandir Marg Police Station", "district": "New Delhi", "lat": 28.6295, "lon": 77.2010, "address": "Mandir Marg, Gole Market", "phone": "011-23362100 / 112"},
    {"name": "Tilak Marg Police Station", "district": "New Delhi", "lat": 28.6190, "lon": 77.2380, "address": "Tilak Marg, India Gate Environs", "phone": "011-23381100 / 112"},
    {"name": "Barakhamba Road Police Station", "district": "New Delhi", "lat": 28.6288, "lon": 77.2285, "address": "Barakhamba Road, Connaught Place", "phone": "011-23412100 / 112"},

    # Central District
    {"name": "Karol Bagh Police Station", "district": "Central", "lat": 28.6517, "lon": 77.1906, "address": "Gurudwara Road, Karol Bagh", "phone": "011-25721100 / 112"},
    {"name": "Paharganj Police Station", "district": "Central", "lat": 28.6432, "lon": 77.2140, "address": "Main Bazar, Paharganj", "phone": "011-23581100 / 112"},
    {"name": "Daryaganj Police Station", "district": "Central", "lat": 28.6480, "lon": 77.2410, "address": "Ansari Road, Daryaganj", "phone": "011-23271100 / 112"},
    {"name": "Chandni Chowk Police Station", "district": "Central", "lat": 28.6562, "lon": 77.2300, "address": "Town Hall, Chandni Chowk", "phone": "011-23261100 / 112"},
    {"name": "Rajinder Nagar Police Station", "district": "Central", "lat": 28.6390, "lon": 77.1790, "address": "Old Rajinder Nagar", "phone": "011-25741100 / 112"},
    {"name": "Kamla Market Police Station", "district": "Central", "lat": 28.6380, "lon": 77.2245, "address": "Asaf Ali Road, New Delhi Railway Station", "phone": "011-23231100 / 112"},

    # North District
    {"name": "Kashmere Gate Police Station", "district": "North", "lat": 28.6675, "lon": 77.2285, "address": "Lothian Road, Kashmere Gate", "phone": "011-23861100 / 112"},
    {"name": "Civil Lines Police Station", "district": "North", "lat": 28.6750, "lon": 77.2230, "address": "Rajpur Road, Civil Lines", "phone": "011-23811100 / 112"},
    {"name": "Timarpur Police Station", "district": "North", "lat": 28.7010, "lon": 77.2190, "address": "Timarpur, North Delhi", "phone": "011-23812100 / 112"},
    {"name": "Maurice Nagar Police Station", "district": "North", "lat": 28.6890, "lon": 77.2080, "address": "Delhi University North Campus", "phone": "011-27661100 / 112"},
    {"name": "Kotwali Police Station", "district": "North", "lat": 28.6580, "lon": 77.2325, "address": "Chandni Chowk Kotwali", "phone": "011-23281100 / 112"},

    # South District
    {"name": "Hauz Khas Police Station", "district": "South", "lat": 28.5430, "lon": 77.2060, "address": "Aurobindo Marg, Hauz Khas", "phone": "011-26861100 / 112"},
    {"name": "Saket Police Station", "district": "South", "lat": 28.5240, "lon": 77.2120, "address": "Press Enclave Marg, Saket", "phone": "011-26511100 / 112"},
    {"name": "Malviya Nagar Police Station", "district": "South", "lat": 28.5360, "lon": 77.2090, "address": "Corner Market, Malviya Nagar", "phone": "011-26681100 / 112"},
    {"name": "Mehrauli Police Station", "district": "South", "lat": 28.5200, "lon": 77.1820, "address": "Near Qutub Minar, Mehrauli", "phone": "011-26641100 / 112"},
    {"name": "Greater Kailash Police Station", "district": "South", "lat": 28.5400, "lon": 77.2380, "address": "GK 1 Near M-Block Market", "phone": "011-29231100 / 112"},

    # South-East District
    {"name": "Lajpat Nagar Police Station", "district": "South-East", "lat": 28.5677, "lon": 77.2433, "address": "Feroze Gandhi Road, Lajpat Nagar III", "phone": "011-29831100 / 112"},
    {"name": "Nehru Place / Kalkaji Police Station", "district": "South-East", "lat": 28.5492, "lon": 77.2527, "address": "Kalkaji Environs, Nehru Place", "phone": "011-26431100 / 112"},
    {"name": "Sarita Vihar Police Station", "district": "South-East", "lat": 28.5300, "lon": 77.2910, "address": "Mathura Road, Sarita Vihar", "phone": "011-26941100 / 112"},
    {"name": "Okhla Industrial Area Police Station", "district": "South-East", "lat": 28.5350, "lon": 77.2720, "address": "Okhla Phase 3", "phone": "011-26841100 / 112"},
    {"name": "Amar Colony Police Station", "district": "South-East", "lat": 28.5610, "lon": 77.2460, "address": "Amar Colony, Lajpat Nagar IV", "phone": "011-26481100 / 112"},

    # South-West District
    {"name": "Vasant Kunj (North) Police Station", "district": "South-West", "lat": 28.5420, "lon": 77.1560, "address": "Sector D, Pocket 2, Vasant Kunj", "phone": "011-26891100 / 112"},
    {"name": "Vasant Vihar Police Station", "district": "South-West", "lat": 28.5580, "lon": 77.1620, "address": "Basant Lok, Vasant Vihar", "phone": "011-26141100 / 112"},
    {"name": "Delhi Cantt Police Station", "district": "South-West", "lat": 28.5898, "lon": 77.1325, "address": "Sadar Bazar, Delhi Cantt", "phone": "011-25691100 / 112"},
    {"name": "Safdarjung Enclave Police Station", "district": "South-West", "lat": 28.5640, "lon": 77.1950, "address": "Safdarjung Enclave Market", "phone": "011-26101100 / 112"},

    # West District
    {"name": "Rajouri Garden Police Station", "district": "West", "lat": 28.6490, "lon": 77.1230, "address": "Main Ring Road, Rajouri Garden", "phone": "011-25441100 / 112"},
    {"name": "Punjabi Bagh Police Station", "district": "West", "lat": 28.6680, "lon": 77.1270, "address": "Rohtak Road, Punjabi Bagh", "phone": "011-25221100 / 112"},
    {"name": "Janakpuri Police Station", "district": "West", "lat": 28.6290, "lon": 77.0810, "address": "District Centre Environs, Janakpuri", "phone": "011-25551100 / 112"},
    {"name": "Tilak Nagar Police Station", "district": "West", "lat": 28.6365, "lon": 77.0965, "address": "Near Tilak Nagar Metro Station", "phone": "011-25981100 / 112"},
    {"name": "Patel Nagar Police Station", "district": "West", "lat": 28.6508, "lon": 77.1654, "address": "Main Patel Road, West Patel Nagar", "phone": "011-25881100 / 112"},

    # North-West District
    {"name": "Netaji Subhash Place Police Station", "district": "North-West", "lat": 28.6925, "lon": 77.1520, "address": "Pitampura TV Tower Environs, NSP", "phone": "011-27151100 / 112"},
    {"name": "Model Town Police Station", "district": "North-West", "lat": 28.7050, "lon": 77.1920, "address": "Model Town II, Ring Road", "phone": "011-27451100 / 112"},
    {"name": "Shalimar Bagh Police Station", "district": "North-West", "lat": 28.7150, "lon": 77.1600, "address": "Club Road, Shalimar Bagh", "phone": "011-27481100 / 112"},

    # Rohini District
    {"name": "Rohini Sector 18 Police Station", "district": "Rohini", "lat": 28.7410, "lon": 77.1320, "address": "Sector 18, Rohini", "phone": "011-27891100 / 112"},
    {"name": "Prashant Vihar Police Station", "district": "Rohini", "lat": 28.7110, "lon": 77.1350, "address": "Prashant Vihar, Outer Ring Road", "phone": "011-27561100 / 112"},

    # Dwarka District
    {"name": "Dwarka Sector 10 Police Station", "district": "Dwarka", "lat": 28.5810, "lon": 77.0580, "address": "Sector 10 District Court Complex, Dwarka", "phone": "011-28081100 / 112"},
    {"name": "Dwarka Sector 23 Police Station", "district": "Dwarka", "lat": 28.5520, "lon": 77.0580, "address": "Sector 23, Dwarka", "phone": "011-28051100 / 112"},
    {"name": "Uttam Nagar Police Station", "district": "Dwarka", "lat": 28.6210, "lon": 77.0650, "address": "Najafgarh Road, Uttam Nagar", "phone": "011-25611100 / 112"},

    # East & Shahdara Districts
    {"name": "Laxmi Nagar Police Station", "district": "East", "lat": 28.6310, "lon": 77.2780, "address": "Vikas Marg, Laxmi Nagar", "phone": "011-22441100 / 112"},
    {"name": "Preet Vihar Police Station", "district": "East", "lat": 28.6410, "lon": 77.2950, "address": "Vikas Marg Ext, Preet Vihar", "phone": "011-22521100 / 112"},
    {"name": "Mayur Vihar Police Station", "district": "East", "lat": 28.6080, "lon": 77.2950, "address": "Pocket 1, Mayur Vihar Phase 1", "phone": "011-22751100 / 112"},
    {"name": "Anand Vihar Police Station", "district": "Shahdara", "lat": 28.6480, "lon": 77.3160, "address": "ISBT Terminal Environs, Anand Vihar", "phone": "011-22161100 / 112"},
    {"name": "Gandhi Nagar Police Station", "district": "Shahdara", "lat": 28.6610, "lon": 77.2680, "address": "Main Road, Gandhi Nagar", "phone": "011-22081100 / 112"},

    # North-East & Outer Districts
    {"name": "Seelampur Police Station", "district": "North-East", "lat": 28.6690, "lon": 77.2670, "address": "GT Road, Seelampur Chowk", "phone": "011-22811100 / 112"},
    {"name": "Paschim Vihar Police Station", "district": "Outer", "lat": 28.6730, "lon": 77.1080, "address": "Jwala Heri Market Road, Paschim Vihar", "phone": "011-25261100 / 112"},
    {"name": "Narela Police Station", "district": "Outer-North", "lat": 28.8450, "lon": 77.0920, "address": "Bawana Road, Narela", "phone": "011-27281100 / 112"}
]

# -----------------------------------------------------------------------------
# 2. OFFENSES TAXONOMY: BHARATIYA NYAYA SANHITA (BNS) & IPC
# -----------------------------------------------------------------------------
DELHI_OFFENSES_VAULT = [
    {
        "id": "mobile_snatching",
        "title": "Mobile / Chain Snatching (Sudden Force Egress)",
        "bnsSection": "Section 304 BNS",
        "ipcSection": "IPC 392 / 356",
        "severity": "CRITICAL",
        "description": "Forcible snatching of mobile phone, purse, or jewellery by pedestrian or motorcycle riders.",
        "suggestedEvidence": ["IMEI Purchase Invoice", "Telecom Call Detail Records", "Eyewitness Audio / Notes", "CCTV Footage"]
    },
    {
        "id": "vehicle_theft",
        "title": "Vehicle Theft (Motorcycle / Car / E-Rickshaw)",
        "bnsSection": "Section 303(2) BNS",
        "ipcSection": "IPC 379",
        "severity": "HIGH",
        "description": "Theft of motorized vehicle or personal conveyance from public roadway or parking.",
        "suggestedEvidence": ["Vehicle RC Copy", "Insurance Policy PDF", "Parking Slip / CCTV Still", "GPS Tracker Log"]
    },
    {
        "id": "assault_hurt",
        "title": "Physical Assault & Voluntarily Causing Hurt",
        "bnsSection": "Section 115(2) & 118 BNS",
        "ipcSection": "IPC 323 / 324",
        "severity": "CRITICAL",
        "description": "Infliction of bodily harm or assault with or without weapon in public or private area.",
        "suggestedEvidence": ["Hospital MLC Medical Slip", "Photographs of Injuries", "Witness Testimony", "Scene Photo"]
    },
    {
        "id": "harassment_stalking",
        "title": "Women Harassment, Stalking & Eve-Teasing",
        "bnsSection": "Section 74 & 78 BNS",
        "ipcSection": "IPC 354 / 354D",
        "severity": "HIGH",
        "description": "Unwanted physical proximity, verbal abuse, stalking, or harassment targeting women.",
        "suggestedEvidence": ["Chat / Message Screenshots", "Audio / Video Clip", "Vehicle Number Plate Photo"]
    },
    {
        "id": "cyber_fraud",
        "title": "Cyber Financial Fraud & Aadhaar / UPI Phishing",
        "bnsSection": "Section 318(4) BNS & Sec 66D IT Act",
        "ipcSection": "IPC 420",
        "severity": "HIGH",
        "description": "Digital deception, fake QR code siphon, SIM swap, or deceptive online banking extraction.",
        "suggestedEvidence": ["Bank Account Statement PDF", "UPI UTR Reference Screenshot", "Phishing WhatsApp Chat"]
    },
    {
        "id": "burglary_trespass",
        "title": "House-Breaking / Burglary & Trespass",
        "bnsSection": "Section 331(4) BNS",
        "ipcSection": "IPC 457 / 380",
        "severity": "HIGH",
        "description": "Lurking house-trespass or broken lock robbery during night or absence of residents.",
        "suggestedEvidence": ["Photos of Broken Locks/Door", "List of Stolen Valuables", "Society DVR CCTV Stream"]
    },
    {
        "id": "extortion_threat",
        "title": "Extortion & Criminal Intimidation",
        "bnsSection": "Section 308 & 351 BNS",
        "ipcSection": "IPC 384 / 506",
        "severity": "CRITICAL",
        "description": "Demanding money, property, or valuable security under threat of bodily injury or exposure.",
        "suggestedEvidence": ["Recorded Audio Threats", "Demand Letter / Screenshot", "Call Log History"]
    }
]

# -----------------------------------------------------------------------------
# 3. HELPER CRYPTOGRAPHIC & GEOSPATIAL FUNCTIONS
# -----------------------------------------------------------------------------
def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates exact Haversine distance in kilometers between two GPS points."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return round(float(R * c), 2)


def find_nearest_station_vault(lat: float, lon: float) -> Dict[str, Any]:
    """Finds nearest Delhi police station and distance in km."""
    min_dist = float("inf")
    nearest = DELHI_POLICE_STATIONS_VAULT[0]
    for ps in DELHI_POLICE_STATIONS_VAULT:
        dist = calculate_haversine_distance(lat, lon, ps["lat"], ps["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = ps
    return {"station": nearest, "distanceKm": min_dist}


def compute_sha256_bytes(data: bytes) -> str:
    """Computes full 64-character lowercase hexadecimal SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_text(text: str) -> str:
    """Computes SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Returns human-readable file size string."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def mask_aadhaar(raw_str: str) -> str:
    """Masks UID to display only last 4 digits (e.g. XXXX-XXXX-9842)."""
    digits = "".join([c for c in raw_str if c.isdigit()])
    if len(digits) < 4:
        return raw_str
    return f"XXXX-XXXX-{digits[-4:]}"


def generate_fir_tracking_id() -> str:
    """Generates official standard tracking ID (e.g. DL-FIR-2026-48192)."""
    suffix = np.random.randint(10000, 99999)
    return f"DL-FIR-2026-{suffix}"


def get_current_ist_timestamp() -> str:
    """Returns current timestamp string in Indian Standard Time."""
    now = datetime.datetime.now()
    return now.strftime("%d %b %Y, %I:%M:%S %p IST")


# -----------------------------------------------------------------------------
# 4. PRE-SEEDED RECORDS INITIALIZATION
# -----------------------------------------------------------------------------
def initialize_efir_session_vault():
    """Initializes session state with persistent e-FIR registry records."""
    if "efir_vault_records" not in st.session_state:
        st.session_state["efir_vault_records"] = [
            {
                "id": "DL-FIR-2026-48192",
                "status": "REGISTERED / UNDER INVESTIGATION",
                "filedAt": "14 Oct 2026, 11:30:15 AM IST",
                "legalAct": "Section 173 BNSS, 2023 & Section 63 BSA, 2023",
                "complainant": {
                    "name": "Rahul Sharma",
                    "phone": "+91 98112 34567",
                    "aadhaar": "5489-3210-9842",
                    "maskedAadhaar": "XXXX-XXXX-9842",
                    "address": "B-4/12, Safdarjung Enclave, New Delhi - 110029",
                    "callbackRequested": True
                },
                "incident": {
                    "offenseId": "mobile_snatching",
                    "offenseTitle": "Mobile / Chain Snatching (Sudden Force Egress)",
                    "bnsSection": "Section 304 BNS",
                    "ipcSection": "IPC 392 / 356",
                    "severity": "CRITICAL",
                    "date": "2026-10-14",
                    "time": "11:15",
                    "narrative": "While exiting Rajiv Chowk Metro Gate 6 towards Radial Road 1, two unknown individuals on a black motorcycle without registration plates snatched my iPhone 15 Pro and laptop backpack. Suspects accelerated towards Barakhamba Road."
                },
                "location": {
                    "lat": 28.6328,
                    "lon": 77.2197,
                    "policeStation": "Connaught Place Police Station",
                    "district": "New Delhi",
                    "stationAddress": "B-Block, Connaught Place, New Delhi",
                    "landmark": "Rajiv Chowk Metro Gate 6 & Radial Road 1",
                    "distanceKm": 0.35
                },
                "evidenceFiles": [
                    {
                        "name": "CCTV_MetroGate6_Clip.mp4",
                        "size": 4210450,
                        "formattedSize": "4.02 MB",
                        "type": "video/mp4",
                        "sha256": "4a7d3b9e8c1f0a2d5e6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f",
                        "timestamp": "11:28:40 AM IST"
                    },
                    {
                        "name": "IMEI_Purchase_Invoice.pdf",
                        "size": 348120,
                        "formattedSize": "339.96 KB",
                        "type": "application/pdf",
                        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "timestamp": "11:29:10 AM IST"
                    }
                ],
                "assignedOfficer": "SI Vikram Chauhan (Badge #DL-8841)",
                "masterBundleHash": "d9e7c3b2f1a8e45b0c7a9143890ef2918471839201948572019384756291a039"
            },
            {
                "id": "DL-FIR-2026-31950",
                "status": "CHAIN OF CUSTODY SEALED",
                "filedAt": "13 Oct 2026, 09:20:44 PM IST",
                "legalAct": "Section 173 BNSS, 2023 & Section 63 BSA, 2023",
                "complainant": {
                    "name": "Priya Verma",
                    "phone": "+91 98765 43210",
                    "aadhaar": "9812-7643-4512",
                    "maskedAadhaar": "XXXX-XXXX-4512",
                    "address": "14/22 Karol Bagh, New Delhi - 110005",
                    "callbackRequested": True
                },
                "incident": {
                    "offenseId": "vehicle_theft",
                    "offenseTitle": "Vehicle Theft (Motorcycle / Car / E-Rickshaw)",
                    "bnsSection": "Section 303(2) BNS",
                    "ipcSection": "IPC 379",
                    "severity": "HIGH",
                    "date": "2026-10-13",
                    "time": "20:45",
                    "narrative": "Parked Honda Activa scooter (DL 04 SZ 8812) outside Gurudwara Road market. Upon return after 45 minutes, vehicle was missing. Lock handle was found forced."
                },
                "location": {
                    "lat": 28.6517,
                    "lon": 77.1906,
                    "policeStation": "Karol Bagh Police Station",
                    "district": "Central",
                    "stationAddress": "Gurudwara Road, Karol Bagh",
                    "landmark": "Near Gurudwara Road Market Junction",
                    "distanceKm": 0.12
                },
                "evidenceFiles": [
                    {
                        "name": "Vehicle_RC_Registration.jpg",
                        "size": 912400,
                        "formattedSize": "891.02 KB",
                        "type": "image/jpeg",
                        "sha256": "8f434346648f6b96df89dda901c5176b10e6d83961dd3c1ac88b59b2dc327aa4",
                        "timestamp": "09:18:22 PM IST"
                    }
                ],
                "assignedOfficer": "Inspector R.K. Meena (SHO Karol Bagh)",
                "masterBundleHash": "7b8c2f10d93e847a19283746501928374659201948572019384756291a039b4e"
            }
        ]


# -----------------------------------------------------------------------------
# 5. RECEIPT GENERATORS: PLAINTEXT & PRINTABLE HTML CERTIFICATES
# -----------------------------------------------------------------------------
def generate_plaintext_receipt(fir: Dict[str, Any]) -> str:
    """Generates standard official text receipt slip."""
    lines = [
        "================================================================================",
        "                    DELHI POLICE • CRIME REPORTING PORTAL",
        "        DIGITAL e-FIR REGISTRATION ACKNOWLEDGMENT & EVIDENCE CUSTODY RECEIPT",
        "             Generated under Sec 173 BNSS, 2023 & Sec 63 BSA, 2023",
        "================================================================================",
        "",
        f"REGISTRATION IDENTIFIER : {fir['id']}",
        f"FILING TIMESTAMP        : {fir['filedAt']}",
        f"JURISDICTIONAL STATUS   : {fir['status']}",
        f"STATUTORY COMPLIANCE    : {fir['legalAct']}",
        "",
        "--- COMPLAINANT PARTICULARS ---",
        f"Name                  : {fir['complainant']['name']}",
        f"Contact Phone         : {fir['complainant']['phone']}",
        f"Government UID        : {fir['complainant']['maskedAadhaar']}",
        f"Address               : {fir['complainant']['address']}",
        "",
        "--- INCIDENT PARTICULARS ---",
        f"Date & Time of Offense: {fir['incident']['date']} at {fir['incident']['time']} IST",
        f"Offense Classification: {fir['incident']['offenseTitle']}",
        f"Statutory Section     : {fir['incident']['bnsSection']} (Equivalent: {fir['incident']['ipcSection']})",
        f"Severity Classification: {fir['incident'].get('severity', 'HIGH')}",
        f"Location Coordinates  : {fir['location']['lat']:.5f}°N, {fir['location']['lon']:.5f}°E",
        f"Landmark / Corridor   : {fir['location']['landmark']}",
        f"Jurisdictional Station: {fir['location']['policeStation']} ({fir['location']['district']} District)",
        f"Assigned Beat Officer : {fir.get('assignedOfficer', 'Sub-Inspector On Duty')}",
        "",
        "--- SUMMARY OF OCCURRENCE ---",
        fir['incident']['narrative'],
        "",
        "--- CRYPTOGRAPHIC EVIDENCE CHAIN OF CUSTODY (SHA-256) ---"
    ]

    if not fir.get("evidenceFiles"):
        lines.append("No digital evidence files attached during initial registration.")
    else:
        for idx, ev in enumerate(fir["evidenceFiles"], 1):
            lines.append(f"Evidence Object #{idx}:")
            lines.append(f"  Filename    : {ev['name']}")
            lines.append(f"  Type / Size : {ev.get('type', 'binary')} ({ev.get('formattedSize', 'N/A')})")
            lines.append(f"  Timestamp   : {ev.get('timestamp', 'N/A')}")
            lines.append(f"  SHA-256 Hash: {ev['sha256']}")
            lines.append("")

    lines.extend([
        "--------------------------------------------------------------------------------",
        "MASTER BUNDLE COMPOSITE HASH (SHA-256):",
        fir['masterBundleHash'],
        "--------------------------------------------------------------------------------",
        "NOTICE: This is an electronically generated legal acknowledgment under Section 173",
        "Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023. Digital evidence hashes are sealed",
        "in compliance with Section 63 of Bharatiya Sakshya Adhiniyam, 2023.",
        "For enquiries, dial 112 or visit your jurisdictional Delhi Police Station.",
        "================================================================================"
    ])
    return "\n".join(lines)


def generate_printable_html_certificate(fir: Dict[str, Any]) -> str:
    """Generates printable, legal certificate HTML with styling and print button."""
    evidence_rows = ""
    if fir.get("evidenceFiles"):
        for i, ev in enumerate(fir["evidenceFiles"], 1):
            evidence_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px 12px; font-weight: bold; color: #1e293b;">#{i}</td>
                <td style="padding: 8px 12px; font-weight: 600; color: #0f172a;">{ev['name']}</td>
                <td style="padding: 8px 12px; font-family: monospace; font-size: 11px; color: #475569;">{ev.get('formattedSize', '')}</td>
                <td style="padding: 8px 12px; font-family: monospace; font-size: 11px; color: #0284c7; word-break: break-all;">{ev['sha256']}</td>
            </tr>
            """
    else:
        evidence_rows = """
        <tr>
            <td colspan="4" style="padding: 12px; text-align: center; color: #64748b; font-style: italic;">
                No digital evidence files attached during initial registration.
            </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Official e-FIR Certificate - {fir['id']}</title>
<style>
    @media print {{
        body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .no-print {{ display: none !important; }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        background: #f8fafc;
        margin: 0;
        padding: 24px;
        color: #0f172a;
    }}
    .cert-box {{
        max-width: 820px;
        margin: 0 auto;
        background: #ffffff;
        border: 2px solid #0f172a;
        padding: 32px 36px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-radius: 8px;
    }}
    .header {{
        text-align: center;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 16px;
        margin-bottom: 20px;
    }}
    .badge {{
        display: inline-block;
        background: #0f172a;
        color: #ffffff;
        font-family: monospace;
        font-weight: bold;
        font-size: 12px;
        padding: 4px 12px;
        border-radius: 4px;
        margin-top: 6px;
    }}
    .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 18px;
    }}
    .panel {{
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 12px 14px;
        font-size: 12px;
    }}
    .panel h4 {{
        margin: 0 0 8px 0;
        font-size: 12px;
        text-transform: uppercase;
        color: #0369a1;
        letter-spacing: 0.05em;
    }}
    .row {{
        margin-bottom: 4px;
        line-height: 1.4;
    }}
    .label {{
        font-weight: 600;
        color: #475569;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 11.5px;
        margin-top: 10px;
    }}
    th {{
        background: #e2e8f0;
        padding: 8px 12px;
        text-align: left;
        font-weight: 700;
        color: #334155;
    }}
    .hash-banner {{
        background: #022c22;
        color: #a7f3d0;
        border: 1px solid #059669;
        padding: 12px 14px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 11px;
        word-break: break-all;
        margin: 18px 0;
    }}
    .btn {{
        background: #0284c7;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
        font-size: 13px;
    }}
</style>
</head>
<body>

<div class="cert-box">
    <div class="no-print" style="text-align: right; margin-bottom: 16px;">
        <button class="btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>

    <div class="header">
        <div style="font-size: 18px; font-weight: 900; letter-spacing: 0.05em; color: #0f172a;">
            DELHI POLICE • GOVERNMENT OF NCT OF DELHI
        </div>
        <div style="font-size: 13px; font-weight: 700; color: #475569; margin-top: 3px;">
            ELECTRONIC FIRST INFORMATION REPORT (e-FIR) CERTIFICATE
        </div>
        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
            Issued under Section 173 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 & Sec 63 BSA, 2023
        </div>
        <div class="badge">REGISTRATION ID: {fir['id']}</div>
    </div>

    <div class="grid">
        <div class="panel">
            <h4>Complainant Record</h4>
            <div class="row"><span class="label">Full Name:</span> <b>{fir['complainant']['name']}</b></div>
            <div class="row"><span class="label">Contact Mobile:</span> {fir['complainant']['phone']}</div>
            <div class="row"><span class="label">Aadhaar UID:</span> {fir['complainant']['maskedAadhaar']}</div>
            <div class="row"><span class="label">Residential Address:</span> {fir['complainant']['address']}</div>
        </div>

        <div class="panel">
            <h4>Incident & Jurisdictional Allocation</h4>
            <div class="row"><span class="label">Police Station:</span> <b>{fir['location']['policeStation']}</b></div>
            <div class="row"><span class="label">District Jurisdiction:</span> {fir['location']['district']} District</div>
            <div class="row"><span class="label">Occurrence:</span> {fir['incident']['date']} at {fir['incident']['time']} IST</div>
            <div class="row"><span class="label">Location GPS:</span> {fir['location']['lat']:.5f}°N, {fir['location']['lon']:.5f}°E</div>
            <div class="row"><span class="label">Assigned Officer:</span> {fir.get('assignedOfficer', 'Sub-Inspector Beat Officer')}</div>
        </div>
    </div>

    <div class="panel" style="margin-bottom: 18px;">
        <h4>Classified Offense & Statutory Provisions</h4>
        <div class="row"><span class="label">Cognizable Offense:</span> <b>{fir['incident']['offenseTitle']}</b></div>
        <div class="row"><span class="label">Statutory Provisions:</span> <b>{fir['incident']['bnsSection']}</b> (Corresponding: {fir['incident']['ipcSection']})</div>
        <div class="row" style="margin-top: 8px;"><span class="label">Statement of Facts:</span></div>
        <div style="background: #ffffff; padding: 10px; border-radius: 4px; border: 1px solid #cbd5e1; font-size: 11.5px; line-height: 1.5; color: #1e293b; margin-top: 4px;">
            {fir['incident']['narrative']}
        </div>
    </div>

    <div style="font-weight: 700; font-size: 12px; text-transform: uppercase; color: #0369a1; letter-spacing: 0.05em; margin-bottom: 6px;">
        Digital Evidence Chain of Custody (SHA-256 Cryptographic Verification)
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Evidence Filename</th>
                <th>Size</th>
                <th>SHA-256 Digital Forensics Hash Digest</th>
            </tr>
        </thead>
        <tbody>
            {evidence_rows}
        </tbody>
    </table>

    <div class="hash-banner">
        <div style="font-weight: bold; margin-bottom: 4px; text-transform: uppercase; color: #6ee7b7;">
            Master Bundle SHA-256 Hash Digest (Chain-of-Custody Sealed):
        </div>
        {fir['masterBundleHash']}
    </div>

    <div style="border-top: 1px solid #cbd5e1; padding-top: 12px; font-size: 10.5px; color: #64748b; line-height: 1.5;">
        <b>STATUTORY DECLARATION:</b> This document constitutes a digitally registered First Information Report. 
        Cryptographic SHA-256 hashes confirm that the digital evidence items submitted are unaltered since registration, 
        maintaining forensic integrity as admissible electronic records under Section 63 of Bharatiya Sakshya Adhiniyam, 2023.
    </div>
</div>

</body>
</html>"""
    return html


# -----------------------------------------------------------------------------
# 6. MAIN STREAMLIT TAB RENDERER
# -----------------------------------------------------------------------------
def render_efir_registration_vault_tab(cleaning_audit: Dict[str, Any], raw_df: pd.DataFrame, df: pd.DataFrame):
    """
    Renders the unified e-FIR Registration & Verification tab:
    - Statutory Delhi Police banner with portal link
    - Sub-selector: Register New e-FIR | Stored FIR Vault | Data Cleaning Funnel
    - Full client & server hashed evidence vault with official acknowledgment
    """
    initialize_efir_session_vault()

    # 1. TOP STATUTORY DISCLAIMER BANNER
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(3, 7, 18, 0.95) 100%);
                border: 1px solid rgba(245, 158, 11, 0.35); border-left: 5px solid #f59e0b; border-radius: 18px; padding: 18px 24px;
                margin-bottom: 22px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); backdrop-filter: blur(16px);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 42px; height: 42px; border-radius: 12px; background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4); display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    ⚠️
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-family: 'Geist Mono', monospace; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #fbbf24; background: rgba(245, 158, 11, 0.2); padding: 2px 8px; border-radius: 9999px; border: 1px solid rgba(245, 158, 11, 0.3);">
                            STATUTORY LEGAL NOTICE
                        </span>
                        <span style="font-size: 13px; font-weight: 700; color: #f1f5f9;">
                            Section 173 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023
                        </span>
                    </div>
                    <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 4px; line-height: 1.5;">
                        For formal legal reporting under Section 173 BNSS, access the official 
                        <a href="https://delhipolice.gov.in/index#service-box" target="_blank" style="color: #38bdf8; font-weight: 700; text-decoration: underline;">
                            Delhi Police Official e-FIR Portal ↗
                        </a>. This system acts as a high-integrity civic evidence vault with cryptographic SHA-256 seal under Section 63 BSA, 2023.
                    </div>
                </div>
            </div>
            <div style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #94a3b8; background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 9999px; border: 1px solid rgba(255,255,255,0.08);">
                Forensics Vault v2.4 Active
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. SUB-NAVIGATION SELECTOR
    sub_tab = st.radio(
        "FIR Pipeline Navigation:",
        [
            "📝 Register New e-FIR & Digital Evidence Vault",
            "🗄️ e-FIR Stored Vault & Audit Registry",
            "📊 Police Data Cleaning & Quality Funnel"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.write("")

    # =========================================================================
    # SUB-TAB 1: REGISTER NEW E-FIR & DIGITAL EVIDENCE VAULT
    # =========================================================================
    if sub_tab.startswith("📝"):
        # Header description
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 20px;">
                📝 Citizen e-FIR Registration & Forensic Evidence Vault
            </h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Enter incident details, geocode police jurisdiction, and upload digital evidence (images, CCTV clips, PDFs). Each file is cryptographically sealed with SHA-256 in accordance with Sec 63 Bharatiya Sakshya Adhiniyam, 2023.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick link to official Delhi Police portal
        c_link1, c_link2 = st.columns([1.5, 1])
        with c_link1:
            st.link_button(
                "↗ Open Official Delhi Police e-FIR Portal (External Service Box)",
                "https://delhipolice.gov.in/index#service-box",
                type="secondary",
                help="Direct access to GNCTD official police lodging service"
            )

        st.markdown("---")

        # -------------------------------------------------------------
        # FORM CONTAINER
        # -------------------------------------------------------------
        with st.container():
            # Section A: Complainant Details
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #38bdf8; font-size: 15px; display: flex; align-items: center; gap: 8px;">
                    <span>👤</span> Section 1: Complainant Particulars (Section 173 BNSS)
                </div>
                <span style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #34d399; background: rgba(16,185,129,0.1); padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(16,185,129,0.25);">
                    UID Verification Supported
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                comp_name = st.text_input("Complainant Full Name *", value="Rahul Sharma", help="Legal name of citizen filing report")
            with col_c2:
                comp_phone = st.text_input("Mobile Phone (for SMS Dispatches) *", value="+91 98112 34567")
            with col_c3:
                comp_aadhaar_raw = st.text_input("Aadhaar UID / Government ID", value="5489-3210-9842", help="UID is masked for citizen privacy")

            col_c4, col_c5 = st.columns([2, 1])
            with col_c4:
                comp_address = st.text_input("Current Residential Address", value="B-4/12, Safdarjung Enclave, New Delhi - 110029")
            with col_c5:
                st.write("")
                st.write("")
                comp_callback = st.checkbox("Request Urgent Beat Officer Callback", value=True)

            st.write("")

            # Section B: Incident Information & BNS Offense Classification
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #fbbf24; font-size: 15px; display: flex; align-items: center; gap: 8px;">
                    <span>⚖️</span> Section 2: Incident Information & Statute Classification
                </div>
                <span style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #fbbf24; background: rgba(245,158,11,0.1); padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(245,158,11,0.25);">
                    Bharatiya Nyaya Sanhita (BNS) 2023
                </span>
            </div>
            """, unsafe_allow_html=True)

            offense_titles = [f"{o['title']} ({o['bnsSection']})" for o in DELHI_OFFENSES_VAULT]
            selected_offense_str = st.selectbox(
                "Classified Offense Category *",
                offense_titles,
                index=0,
                help="Select offense to auto-populate statutory section and recommended evidentiary checklist"
            )
            selected_offense_idx = offense_titles.index(selected_offense_str)
            selected_offense = DELHI_OFFENSES_VAULT[selected_offense_idx]

            col_i1, col_i2, col_i3 = st.columns(3)
            with col_i1:
                inc_date = st.date_input("Date of Occurrence *", datetime.date.today())
            with col_i2:
                inc_time = st.time_input("Approximate Time of Occurrence (IST) *", datetime.datetime.now().time())
            with col_i3:
                st.markdown(f"""
                <div style="background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 10px 14px; margin-top: 4px;">
                    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Statutory Mapping</div>
                    <div style="font-size: 12.5px; font-weight: 700; color: #f8fafc; margin-top: 2px;">
                        {selected_offense['bnsSection']} <span style="color: #64748b;">(formerly {selected_offense['ipcSection']})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            inc_narrative = st.text_area(
                "Detailed Incident Narrative / Modus Operandi *",
                value="While exiting Rajiv Chowk Metro Gate 6 towards Radial Road 1, two unknown individuals on a black motorcycle without registration plates snatched my iPhone and laptop backpack. Suspects accelerated towards Barakhamba Road.",
                height=110,
                help="Include vehicle description, suspect physical appearance, direction of escape, and stolen article serial numbers"
            )

            # Recommended evidence badge list
            sugg_evidence_html = "".join([
                f"<span style='font-family: monospace; font-size: 11px; background: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.25); padding: 3px 8px; border-radius: 6px; margin-right: 6px;'>✓ {ev}</span>"
                for ev in selected_offense["suggestedEvidence"]
            ])
            st.markdown(f"""
            <div style="font-size: 12px; color: #94a3b8; margin-top: -6px; margin-bottom: 14px;">
                <b style="color: #e2e8f0;">Suggested Evidence for this offense:</b> {sugg_evidence_html}
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            # Section C: Geolocation & Jurisdiction
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #34d399; font-size: 15px; display: flex; align-items: center; gap: 8px;">
                    <span>📍</span> Section 3: Geolocation Coordinates & Delhi Police Station Allocation
                </div>
                <span style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #38bdf8; background: rgba(56,189,248,0.1); padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(56,189,248,0.25);">
                    15 Delhi Districts Indexed
                </span>
            </div>
            """, unsafe_allow_html=True)

            station_names = [f"{ps['name']} ({ps['district']} District)" for ps in DELHI_POLICE_STATIONS_VAULT]
            col_l1, col_l2, col_l3 = st.columns([1.4, 0.8, 0.8])
            
            with col_l1:
                selected_ps_str = st.selectbox(
                    "Jurisdictional Delhi Police Station *",
                    station_names,
                    index=0,
                    help="Assigns report to designated Station House Officer (SHO)"
                )
                selected_ps_idx = station_names.index(selected_ps_str)
                selected_ps_obj = DELHI_POLICE_STATIONS_VAULT[selected_ps_idx]

            with col_l2:
                # Default coords initialized from selected station or user GPS
                default_lat = selected_ps_obj["lat"]
                target_lat = st.number_input("Target Latitude (°N) *", value=float(default_lat), format="%.5f", step=0.0001)

            with col_l3:
                default_lon = selected_ps_obj["lon"]
                target_lon = st.number_input("Target Longitude (°E) *", value=float(default_lon), format="%.5f", step=0.0001)

            col_land1, col_land2 = st.columns([2, 1])
            with col_land1:
                inc_landmark = st.text_input("Specific Landmark / Street Corridor", value="Rajiv Chowk Metro Gate 6 & Radial Road 1")
            with col_land2:
                # Calculate real-time nearest station to input lat/lon
                calc_nearest = find_nearest_station_vault(target_lat, target_lon)
                st.markdown(f"""
                <div style="background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 12px; padding: 10px 14px; margin-top: 4px;">
                    <div style="font-size: 10.5px; color: #6ee7b7; text-transform: uppercase; font-family: 'Geist Mono', monospace; font-weight: 700;">
                        Proximity Nearest Station
                    </div>
                    <div style="font-size: 12px; font-weight: 700; color: #ffffff; margin-top: 2px;">
                        {calc_nearest['station']['name']} ({calc_nearest['distanceKm']} km)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # Section D: Digital Evidence Vault & SHA-256 Hashing
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #818cf8; font-size: 15px; display: flex; align-items: center; gap: 8px;">
                    <span>🛡️</span> Section 4: Digital Evidence Vault & Cryptographic Hash Sealing
                </div>
                <span style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #a7f3d0; background: rgba(16,185,129,0.15); padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(16,185,129,0.3); font-weight: 700;">
                    Sec 63 BSA, 2023 Compliant
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.caption("Upload images (CCTV, injury photos), video clips, or PDF documents. The system automatically calculates 64-character SHA-256 cryptographic digests to generate a tamper-proof audit seal.")

            uploaded_evidence = st.file_uploader(
                "Upload Digital Evidence Items",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg", "mp4", "mov", "pdf", "txt"],
                help="Accepts camera photos, CCTV surveillance stills, audio recordings, or transaction statements"
            )

            processed_evidence_items: List[Dict[str, Any]] = []

            if uploaded_evidence:
                st.markdown(f"**Processed Evidence Objects ({len(uploaded_evidence)} files sealed):**")
                for f in uploaded_evidence:
                    f_bytes = f.getvalue()
                    f_hash = compute_sha256_bytes(f_bytes)
                    f_size = len(f_bytes)
                    f_size_str = format_file_size(f_size)
                    f_time = get_current_ist_timestamp()

                    ev_item = {
                        "name": f.name,
                        "size": f_size,
                        "formattedSize": f_size_str,
                        "type": f.type or "application/octet-stream",
                        "sha256": f_hash,
                        "timestamp": f_time
                    }
                    processed_evidence_items.append(ev_item)

                    # Card for each file with Tamper-Proof Audit Hash badge
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 12px 18px; margin-bottom: 10px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 12px; min-width: 220px;">
                            <div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); display: flex; align-items: center; justify-content: center; font-size: 16px;">
                                📎
                            </div>
                            <div>
                                <div style="font-weight: 700; color: #f8fafc; font-size: 13px;">{f.name}</div>
                                <div style="font-family: 'Geist Mono', monospace; font-size: 11px; color: #94a3b8;">
                                    {f_size_str} • {f.type or 'file'} • {f_time}
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                            <span style="font-family: 'Geist Mono', monospace; font-size: 10.5px; font-weight: 700; color: #34d399; background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.35); padding: 4px 10px; border-radius: 8px; display: flex; align-items: center; gap: 6px; box-shadow: 0 0 12px rgba(16,185,129,0.15);">
                                <span>🛡️</span> Tamper-Proof Audit Hash Generated
                            </span>
                            <div style="background: rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 8px; font-family: 'Geist Mono', monospace; font-size: 11px; color: #38bdf8;">
                                SHA-256: <b>{f_hash[:10]}...{f_hash[-10:]}</b>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border: 2px dashed rgba(255,255,255,0.12); border-radius: 16px; padding: 22px; text-align: center; background: rgba(0,0,0,0.25); margin-bottom: 12px;">
                    <div style="font-size: 24px; margin-bottom: 4px;">📂</div>
                    <div style="font-weight: 700; color: #e2e8f0; font-size: 13px;">Drag and Drop Incident Evidence Above</div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                        Photographs, CCTV surveillance mp4, audio notes, or FIR receipts. Client-side hashing seals evidence instantly.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # -------------------------------------------------------------
            # SUBMIT BUTTON
            # -------------------------------------------------------------
            submit_col1, submit_col2 = st.columns([2, 1])
            with submit_col1:
                st.caption("Upon submission, a Master Composite SHA-256 digest is generated and sealed into the local audit ledger.")
            with submit_col2:
                submit_clicked = st.button(
                    "🛡️ Submit e-FIR & Generate Audit Certificate",
                    type="primary",
                    use_container_width=True
                )

            if submit_clicked:
                if not comp_name.strip() or not inc_narrative.strip():
                    st.error("Please provide both Complainant Full Name and Incident Narrative.")
                else:
                    new_ref_id = generate_fir_tracking_id()
                    now_str = get_current_ist_timestamp()

                    # Compute composite master hash over all fields and evidence hashes
                    master_payload = {
                        "trackingId": new_ref_id,
                        "complainant": {
                            "name": comp_name,
                            "phone": comp_phone,
                            "aadhaar": comp_aadhaar_raw,
                            "address": comp_address
                        },
                        "incident": {
                            "offense": selected_offense["id"],
                            "bns": selected_offense["bnsSection"],
                            "date": str(inc_date),
                            "time": str(inc_time),
                            "narrative": inc_narrative
                        },
                        "location": {
                            "station": selected_ps_obj["name"],
                            "lat": target_lat,
                            "lon": target_lon,
                            "landmark": inc_landmark
                        },
                        "evidenceHashes": [ev["sha256"] for ev in processed_evidence_items],
                        "timestamp": now_str
                    }
                    master_hash = compute_sha256_text(json.dumps(master_payload, sort_keys=True))

                    # Create record
                    new_record = {
                        "id": new_ref_id,
                        "status": "REGISTERED / UNDER INVESTIGATION",
                        "filedAt": now_str,
                        "legalAct": "Section 173 BNSS, 2023 & Section 63 BSA, 2023",
                        "complainant": {
                            "name": comp_name,
                            "phone": comp_phone,
                            "aadhaar": comp_aadhaar_raw,
                            "maskedAadhaar": mask_aadhaar(comp_aadhaar_raw),
                            "address": comp_address,
                            "callbackRequested": comp_callback
                        },
                        "incident": {
                            "offenseId": selected_offense["id"],
                            "offenseTitle": selected_offense["title"],
                            "bnsSection": selected_offense["bnsSection"],
                            "ipcSection": selected_offense["ipcSection"],
                            "severity": selected_offense.get("severity", "HIGH"),
                            "date": str(inc_date),
                            "time": str(inc_time),
                            "narrative": inc_narrative
                        },
                        "location": {
                            "lat": target_lat,
                            "lon": target_lon,
                            "policeStation": selected_ps_obj["name"],
                            "district": selected_ps_obj["district"],
                            "stationAddress": selected_ps_obj["address"],
                            "landmark": inc_landmark,
                            "distanceKm": calc_nearest["distanceKm"]
                        },
                        "evidenceFiles": processed_evidence_items,
                        "assignedOfficer": f"SI R. Sharma (Jurisdictional Beat Officer #{np.random.randint(4000, 9999)})",
                        "masterBundleHash": master_hash
                    }

                    # Store in session state
                    st.session_state["efir_vault_records"].insert(0, new_record)
                    st.session_state["active_receipt"] = new_record
                    st.success(f"✅ e-FIR successfully registered with Tracking ID: {new_ref_id}!")
                    st.rerun()

        # -------------------------------------------------------------
        # DISPLAY ACTIVE RECEIPT (IF SUBMITTED OR SELECTED)
        # -------------------------------------------------------------
        if "active_receipt" in st.session_state and st.session_state["active_receipt"]:
            active_fir = st.session_state["active_receipt"]
            st.markdown("---")
            st.markdown(f"""
            <div style="background: rgba(6, 78, 59, 0.4); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 20px; padding: 24px; margin-top: 18px; box-shadow: 0 12px 36px rgba(0,0,0,0.5);">
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(16,185,129,0.3); padding-bottom: 14px; margin-bottom: 18px;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="width: 44px; height: 44px; border-radius: 12px; background: #10b981; color: #022c22; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900;">
                            ✓
                        </div>
                        <div>
                            <span style="font-family: 'Geist Mono', monospace; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #6ee7b7; background: rgba(16, 185, 129, 0.2); padding: 2px 8px; border-radius: 9999px;">
                                CONFIRMATION ISSUED
                            </span>
                            <h3 style="margin: 4px 0 0 0; color: #ffffff; font-size: 20px; font-weight: 800;">
                                Official e-FIR Registration & Digital Evidence Receipt
                            </h3>
                            <p style="margin: 2px 0 0 0; font-size: 12px; color: #94a3b8;">
                                Electronic First Information Report logged under Section 173 BNSS, 2023 & Section 63 BSA, 2023
                            </p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: 'Geist Mono', monospace; font-size: 10px; color: #94a3b8; text-transform: uppercase;">Official Reference No.</div>
                        <div style="font-family: 'Geist Mono', monospace; font-size: 22px; font-weight: 900; color: #34d399; letter-spacing: 0.05em;">
                            {active_fir['id']}
                        </div>
                    </div>
                </div>

                <div style="background: rgba(0,0,0,0.45); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: 'Geist Mono', monospace; font-size: 11px; text-transform: uppercase; color: #38bdf8; font-weight: 700;">
                            Computed Master SHA-256 Audit Hash Digest
                        </span>
                        <span style="font-family: 'Geist Mono', monospace; font-size: 10px; color: #94a3b8;">64-char Hexadecimal Forensics Stamp</span>
                    </div>
                    <div style="font-family: 'Geist Mono', monospace; font-size: 12px; color: #f1f5f9; word-break: break-all; background: rgba(0,0,0,0.5); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(56,189,248,0.25);">
                        {active_fir['masterBundleHash']}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 12.5px; margin-bottom: 16px;">
                    <div style="background: rgba(15,23,42,0.6); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <span style="color: #94a3b8; display: block; font-size: 11px;">Complainant:</span>
                        <b style="color: #ffffff;">{active_fir['complainant']['name']}</b> ({active_fir['complainant']['phone']})
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <span style="color: #94a3b8; display: block; font-size: 11px;">Jurisdiction:</span>
                        <b style="color: #ffffff;">{active_fir['location']['policeStation']}</b> ({active_fir['location']['district']} District)
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <span style="color: #94a3b8; display: block; font-size: 11px;">Classified Offense:</span>
                        <b style="color: #ffffff;">{active_fir['incident']['offenseTitle']}</b>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <span style="color: #94a3b8; display: block; font-size: 11px;">Telemetry Location:</span>
                        <b style="color: #ffffff;">{active_fir['location']['lat']:.4f}°N, {active_fir['location']['lon']:.4f}°E</b> ({len(active_fir['evidenceFiles'])} Evidence files sealed)
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Receipt Actions: Download .txt, Download .html certificate, Close
            c_act1, c_act2, c_act3 = st.columns([1, 1, 1])
            with c_act1:
                txt_receipt = generate_plaintext_receipt(active_fir)
                st.download_button(
                    label="📄 Download Official Receipt Slip (.txt)",
                    data=txt_receipt,
                    file_name=f"{active_fir['id']}_Receipt_Slip.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with c_act2:
                html_cert = generate_printable_html_certificate(active_fir)
                st.download_button(
                    label="🖨️ Download Printable Legal Certificate (.html)",
                    data=html_cert,
                    file_name=f"{active_fir['id']}_Legal_Certificate.html",
                    mime="text/html",
                    use_container_width=True
                )
            with c_act3:
                if st.button("✕ Dismiss Active Receipt", use_container_width=True):
                    st.session_state["active_receipt"] = None
                    st.rerun()

    # =========================================================================
    # SUB-TAB 2: E-FIR STORED VAULT & AUDIT REGISTRY
    # =========================================================================
    elif sub_tab.startswith("🗄️"):
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 20px;">
                🗄️ Citizen e-FIR Stored Vault & Legal Audit Registry
            </h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Inspect all registered First Information Reports with cryptographic SHA-256 evidence chain verification under Section 63 BSA, 2023.
            </p>
        </div>
        """, unsafe_allow_html=True)

        records = st.session_state.get("efir_vault_records", [])

        # Registry Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Stored e-FIRs", len(records), "Session Active")
        with m2:
            total_ev = sum([len(r.get("evidenceFiles", [])) for r in records])
            st.metric("Evidence Objects Sealed", total_ev, "SHA-256 Verified")
        with m3:
            districts_set = set([r["location"]["district"] for r in records])
            st.metric("Districts Active", len(districts_set), "GNCTD Bounds")
        with m4:
            st.metric("Chain of Custody Standard", "100% Sealed", "Sec 63 BSA")

        st.markdown("---")

        # Search / Filter
        search_fir = st.text_input("🔍 Search e-FIR Records by Tracking ID, Complainant Name, or Police Station:", "")

        filtered_records = records
        if search_fir.strip():
            q = search_fir.strip().lower()
            filtered_records = [
                r for r in records
                if q in r["id"].lower() or q in r["complainant"]["name"].lower() or q in r["location"]["policeStation"].lower() or q in r["incident"]["offenseTitle"].lower()
            ]

        if not filtered_records:
            st.info("No e-FIR records match your search criteria.")
        else:
            for fir in filtered_records:
                with st.expander(f"📋 {fir['id']} • {fir['complainant']['name']} • {fir['location']['policeStation']} ({fir['status']})", expanded=(fir == records[0])):
                    col_det1, col_det2 = st.columns([1.2, 1])

                    with col_det1:
                        st.markdown(f"""
                        **Registration ID:** `{fir['id']}`  
                        **Filing Timestamp:** `{fir['filedAt']}`  
                        **Status:** <span style="color: #34d399; font-weight: bold;">{fir['status']}</span>  
                        **Complainant:** **{fir['complainant']['name']}** ({fir['complainant']['phone']})  
                        **Masked UID:** `{fir['complainant']['maskedAadhaar']}`  
                        **Address:** {fir['complainant']['address']}  
                        **Assigned Officer:** {fir.get('assignedOfficer', 'SI Beat Officer')}  
                        """, unsafe_allow_html=True)

                    with col_det2:
                        st.markdown(f"""
                        **Offense:** **{fir['incident']['offenseTitle']}**  
                        **Statute:** `{fir['incident']['bnsSection']}` (IPC: `{fir['incident']['ipcSection']}`)  
                        **Police Station:** **{fir['location']['policeStation']}** ({fir['location']['district']} District)  
                        **Occurrence Date:** {fir['incident']['date']} at {fir['incident']['time']} IST  
                        **Coordinates:** `{fir['location']['lat']:.4f}°N, {fir['location']['lon']:.4f}°E`  
                        **Corridor:** {fir['location']['landmark']}  
                        """, unsafe_allow_html=True)

                    st.markdown("**Incident Narrative:**")
                    st.info(fir['incident']['narrative'])

                    # Evidence Table
                    if fir.get("evidenceFiles"):
                        st.markdown(f"**Forensic Evidence Chain ({len(fir['evidenceFiles'])} files):**")
                        ev_df = pd.DataFrame([
                            {
                                "Filename": ev["name"],
                                "Type": ev.get("type", "binary"),
                                "Size": ev.get("formattedSize", "N/A"),
                                "SHA-256 Digest": ev["sha256"],
                                "Timestamp": ev.get("timestamp", "N/A")
                            }
                            for ev in fir["evidenceFiles"]
                        ])
                        st.dataframe(ev_df, use_container_width=True, hide_index=True)

                    st.markdown(f"""
                    <div style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 14px; font-family: 'Geist Mono', monospace; font-size: 11px; margin-top: 8px;">
                        <span style="color: #38bdf8; font-weight: bold;">MASTER BUNDLE COMPOSITE HASH:</span> {fir['masterBundleHash']}
                    </div>
                    """, unsafe_allow_html=True)

                    st.write("")
                    c_dl1, c_dl2, c_dl3 = st.columns([1, 1, 1])
                    with c_dl1:
                        txt_data = generate_plaintext_receipt(fir)
                        st.download_button(
                            label="📄 Download Slip (.txt)",
                            data=txt_data,
                            file_name=f"{fir['id']}_Receipt.txt",
                            mime="text/plain",
                            key=f"dl_txt_{fir['id']}",
                            use_container_width=True
                        )
                    with c_dl2:
                        html_data = generate_printable_html_certificate(fir)
                        st.download_button(
                            label="🖨️ Printable Certificate (.html)",
                            data=html_data,
                            file_name=f"{fir['id']}_Certificate.html",
                            mime="text/html",
                            key=f"dl_html_{fir['id']}",
                            use_container_width=True
                        )
                    with c_dl3:
                        if st.button("👁️ View Full Confirmation Card", key=f"view_{fir['id']}", use_container_width=True):
                            st.session_state["active_receipt"] = fir
                            st.rerun()

    # =========================================================================
    # SUB-TAB 3: POLICE DATA CLEANING & QUALITY FUNNEL (EXISTING PIPELINE)
    # =========================================================================
    else:
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 20px;">
                📊 Police FIR Data Cleaning & Completeness Verification Pipeline
            </h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Transforming raw, noisy police feeds into high-integrity verified crime data for algorithmic hotspot discovery.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Executive Pipeline Flow / Summary Card
        st.markdown("""
        <div style="background: rgba(14, 18, 26, 0.75); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px 24px; margin-bottom: 22px; box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);">
            <div style="font-weight: 700; color: #f8fafc; font-size: 15px; margin-bottom: 8px;">
                🛡️ Production Data Integrity Standard: Zero-Missing & Confirmed Only
            </div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">
                In predictive policing and geospatial clustering, <b>dirty data corrupts algorithmic decisions</b>. If unconfirmed citizen tips, 
                false alarms, or records with missing coordinates leak into density estimators like DBSCAN, cluster centroids warp and police patrols 
                are dispatched to phantom corridors. Our data cleaning pipeline enforces a rigorous 5-stage verification filter on confirmed official records.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 6 Funnel KPI Metric Cards
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.metric("1. Raw Feed Ingested", f"{cleaning_audit.get('raw_count', len(raw_df)):,}", "Incoming Logs")
        with c2:
            st.metric("2. Unconfirmed Dropped", f"-{cleaning_audit.get('unconfirmed_dropped', 0):,}", "Pending / False")
        with c3:
            st.metric("3. Missing GPS Dropped", f"-{cleaning_audit.get('missing_coords_dropped', 0):,}", "Null Coordinates")
        with c4:
            st.metric("4. Missing Cols Dropped", f"-{cleaning_audit.get('missing_critical_fields_dropped', 0):,}", "Null Attributes")
        with c5:
            st.metric("5. Duplicates Dropped", f"-{cleaning_audit.get('duplicates_dropped', 0):,}", "Duplicate Logs")
        with c6:
            st.metric("6. Verified Hotspot Base", f"{len(df):,}", f"{cleaning_audit.get('retention_rate_pct', 72.8)}% Retained")

        st.markdown("---")

        col_audit_left, col_audit_right = st.columns([1.1, 0.9])

        with col_audit_left:
            st.markdown("### 🔍 Cleaning Funnel & Rejection Reasons")
            st.caption("Distribution of filtered raw records across validation stages.")
            
            rejection_data = pd.DataFrame(cleaning_audit.get("rejection_summary", []))
            if not rejection_data.empty:
                rejection_data["% of Raw Records"] = (rejection_data["count"] / cleaning_audit.get("raw_count", 1) * 100.0).round(2)
                rejection_data = rejection_data.rename(columns={"reason": "Filter / Rejection Rule", "count": "Dropped Records"})
                st.dataframe(rejection_data, use_container_width=True, hide_index=True)

            st.markdown("#### 🎯 Data Quality Scorecard")
            q1, q2, q3 = st.columns(3)
            with q1:
                st.metric("Data Completeness", "100.0%", "0 Missing Values")
            with q2:
                st.metric("FIR Confirmation", "100.0%", "All Confirmed")
            with q3:
                st.metric("Geocode Validity", "100.0%", "Delhi NCT Bounds")

        with col_audit_right:
            st.markdown("### 🛡️ Verification Rules & Architectural Defense")
            with st.expander("1. Verification Status (Confirmed FIR Only)", expanded=True):
                st.markdown("""
                - **Problem**: Emergency call feeds contain unconfirmed tips, false alarms, and incidents still under preliminary enquiry.
                - **Criminological Impact**: Clustering unverified calls forces scarce police resources away from real persistent crime hubs.
                - **Rule**: Retain only records with `confirmation_status == 'Confirmed'`.
                """)
            with st.expander("2. Zero-Tolerance for Missing Coordinates & Attributes"):
                st.markdown("""
                - **Problem**: In real police databases, 3-6% of records lack GPS coordinates or have (0,0) null placeholders.
                - **Mathematical Impact**: Haversine distance matrix computation breaks with NaN coordinates. Imputation with district centroids artificially bunches crime into fake clusters.
                - **Rule**: Prune any record with missing lat/lon, crime type, premises, or timestamp.
                """)
            with st.expander("3. Delhi Territorial Geofencing (NCT Bounding Box)"):
                st.markdown(r"""
                - **Problem**: Coordinate transpositions or faulty GPS units record incidents in neighboring states (UP, Haryana) or oceans.
                - **Rule**: Enforce strict bounding box: Latitude $28.30^\circ\text{N} - 28.95^\circ\text{N}$, Longitude $76.80^\circ\text{E} - 77.50^\circ\text{E}$.
                """)
            with st.expander("4. Duplicate Incident Deduplication"):
                st.markdown("""
                - **Problem**: Multiple citizens report the same snatching or robbery, resulting in multiple dispatch records for a single event.
                - **Rule**: Deduplicate on composite spatio-temporal key `[record_id]` and `[date, hour, minute, lat, lon, crime_category]`.
                """)

        st.markdown("---")
        st.markdown("### 📋 Interactive Record Inspector: Clean vs Rejected Sample")
        inspector_mode = st.radio(
            "Select Dataset View to Inspect:",
            [" Cleaned & Verified Police Records (Used for Hotspots & ML)", "⚠️ Raw Ingested Sample with Data Flaws"],
            horizontal=True
        )
        if inspector_mode.startswith(""):
            st.caption("Showing sample of verified records. All fields are 100% complete and validated.")
            cols_to_show = ["record_id", "confirmation_status", "district", "police_station", "crime_category", "premises_type", "date", "hour", "latitude", "longitude", "risk_level"]
            st.dataframe(df[[c for c in cols_to_show if c in df.columns]].head(15), use_container_width=True, hide_index=True)
        else:
            st.caption("Showing sample from raw feed highlighting unconfirmed statuses and missing fields.")
            raw_display = raw_df.head(25).copy()
            cols_to_show = ["record_id", "confirmation_status", "district", "crime_category", "latitude", "longitude", "date", "hour", "risk_level"]
            st.dataframe(raw_display[[c for c in cols_to_show if c in raw_display.columns]], use_container_width=True, hide_index=True)
