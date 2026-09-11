# Delhi Historical Crime Dataset (2015-2025)

## Overview
This directory stores historical crime records for the National Capital Territory of Delhi, used by **Rakshak.ai** for spatiotemporal crime hotspot detection, DBSCAN spatial clustering, and machine learning risk forecasting.

## Dataset Attributes
- `crime_id`: Unique alphanumeric incident identifier (e.g., `DL-2015-015031`)
- `timestamp`: Combined incident datetime (`YYYY-MM-DD HH:MM:SS`)
- `date`: Incident date (`YYYY-MM-DD`)
- `time`: Incident time (`HH:MM`)
- `year`: Incident year (`2015` to `2025`)
- `month`: Incident month (`1` to `12`)
- `day_of_week`: Day name (`Monday` to `Sunday`)
- `hour`: Incident hour (`0` to `23`)
- `crime_type`: Primary offense category (e.g., Motor Vehicle Theft, Snatching, Burglary, Robbery, Assault / Hurt, Pickpocketing)
- `ipc_bns_section`: Corresponding legal statute (Indian Penal Code or Bharatiya Nyaya Sanhita)
- `severity_score`: Offense severity rating from `1` (minor theft) to `5` (heinous / armed violent crime)
- `district`: Delhi Police Administrative District (Central, North, South, South West, Shahdara, North East, New Delhi, Outer North, etc.)
- `police_station`: Jurisdiction police station
- `location_name`: Landmark, market, or road identifier
- `location_type`: Environmental categorization (Commercial Market, Transit Hub, Residential Colony, Highway, etc.)
- `latitude`: Geospatial latitude coordinate
- `longitude`: Geospatial longitude coordinate
- `weapon_used`: Indicates if a weapon was involved (`Yes` / `No`)
- `investigation_status`: Legal status (`Under Investigation`, `Chargesheet Filed`, `Untraced`, `Convicted`)
