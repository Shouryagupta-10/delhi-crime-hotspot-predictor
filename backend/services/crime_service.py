import math
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models import CrimeRecord
from schemas import CrimeRecordCreate, CrimeFilterParams


def get_crimes(
    db: Session,
    filters: Optional[CrimeFilterParams] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Query crime records with filtering, pagination, and sorting.
    """
    query = db.query(CrimeRecord)

    if filters:
        if filters.district:
            query = query.filter(CrimeRecord.district.ilike(f"%{filters.district}%"))
        if filters.crime_type:
            query = query.filter(CrimeRecord.crime_type.ilike(f"%{filters.crime_type}%"))
        if filters.year:
            query = query.filter(CrimeRecord.year == filters.year)
        if filters.month:
            query = query.filter(CrimeRecord.month == filters.month)
        if filters.min_severity:
            query = query.filter(CrimeRecord.severity_score >= filters.min_severity)
        if filters.police_station:
            query = query.filter(CrimeRecord.police_station.ilike(f"%{filters.police_station}%"))
        if filters.start_date:
            query = query.filter(CrimeRecord.date >= filters.start_date)
        if filters.end_date:
            query = query.filter(CrimeRecord.date <= filters.end_date)

    total_records = query.count()
    total_pages = math.ceil(total_records / page_size) if page_size > 0 else 1

    records = (
        query.order_by(desc(CrimeRecord.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total_records": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "data": records
    }


def get_crime_by_id(db: Session, crime_id: str) -> Optional[CrimeRecord]:
    """
    Retrieve a single crime incident by unique ID.
    """
    return db.query(CrimeRecord).filter(CrimeRecord.crime_id == crime_id).first()


def create_crime_record(db: Session, crime_in: CrimeRecordCreate) -> CrimeRecord:
    """
    Insert a new crime incident record into SQLite.
    """
    crime_data = crime_in.model_dump()
    if not crime_data.get("crime_id"):
        crime_data["crime_id"] = f"DL-{crime_data['year']}-{uuid.uuid4().hex[:6].upper()}"

    db_record = CrimeRecord(**crime_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_crime_summary_stats(db: Session) -> Dict[str, Any]:
    """
    Generate aggregate metrics for the Delhi crime analytics dashboard.
    """
    total_crimes = db.query(func.count(CrimeRecord.crime_id)).scalar() or 0
    high_severity_crimes = db.query(func.count(CrimeRecord.crime_id)).filter(CrimeRecord.severity_score >= 4).scalar() or 0
    districts_count = db.query(func.count(func.distinct(CrimeRecord.district))).scalar() or 0

    top_districts = (
        db.query(CrimeRecord.district, func.count(CrimeRecord.crime_id).label("count"))
        .group_by(CrimeRecord.district)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    top_crime_types = (
        db.query(CrimeRecord.crime_type, func.count(CrimeRecord.crime_id).label("count"))
        .group_by(CrimeRecord.crime_type)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    return {
        "total_crimes": total_crimes,
        "high_severity_crimes": high_severity_crimes,
        "districts_count": districts_count,
        "top_districts": [{"district": d[0], "count": d[1]} for d in top_districts],
        "top_crime_types": [{"crime_type": c[0], "count": c[1]} for c in top_crime_types],
    }


def get_nearby_crimes(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 2.0,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Find crime incidents within a specified radius (km) from coordinates using the Haversine spherical distance metric.
    Calculates detailed nearby crime statistics, severity breakdown, and overlaps with detected DBSCAN hotspots.
    """
    import math
    from collections import Counter
    from services import hotspot

    EARTH_RADIUS_KM = 6371.0088

    # Fast rectangular bounding-box pre-filtering
    lat_delta = radius_km / 111.0
    cos_lat = max(0.01, math.cos(math.radians(latitude)))
    lon_delta = radius_km / (111.0 * cos_lat)

    candidates = db.query(CrimeRecord).filter(
        CrimeRecord.latitude.between(latitude - lat_delta, latitude + lat_delta),
        CrimeRecord.longitude.between(longitude - lon_delta, longitude + lon_delta)
    ).all()

    matched_records = []
    lat1_rad = math.radians(latitude)

    for rec in candidates:
        dlat = math.radians(rec.latitude - latitude)
        dlon = math.radians(rec.longitude - longitude)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(lat1_rad) * math.cos(math.radians(rec.latitude)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.asin(min(1.0, math.sqrt(a)))
        dist = EARTH_RADIUS_KM * c

        if dist <= radius_km:
            matched_records.append((dist, rec))

    # Sort by distance ascending
    matched_records.sort(key=lambda x: x[0])
    total_matched = len(matched_records)

    # Compute summary analytics
    if total_matched > 0:
        avg_sev = round(sum(r[1].severity_score for r in matched_records) / total_matched, 2)
        high_sev = sum(1 for r in matched_records if r[1].severity_score >= 4)
        high_sev_pct = round((high_sev / total_matched) * 100.0, 1)

        crime_counts = Counter(r[1].crime_type for r in matched_records)
        most_common = crime_counts.most_common(1)[0][0]
        breakdown = [
            {"crime_type": k, "count": v, "percentage": round((v / total_matched) * 100.0, 1)}
            for k, v in crime_counts.most_common()
        ]
        sev_dist = dict(Counter(str(r[1].severity_score) for r in matched_records))
    else:
        avg_sev = 0.0
        high_sev = 0
        high_sev_pct = 0.0
        most_common = None
        breakdown = []
        sev_dist = {}

    # Check for nearby DBSCAN hotspots
    nearby_hotspots_count = 0
    try:
        hotspots_res = hotspot.detect_crime_hotspots(db, eps_km=0.5, min_samples=25)
        for h in hotspots_res.get("hotspots", []):
            h_lat = h.get("center_latitude", 0.0)
            h_lon = h.get("center_longitude", 0.0)
            h_rad_km = (h.get("radius_meters", 500.0) or 500.0) / 1000.0

            dlat = math.radians(h_lat - latitude)
            dlon = math.radians(h_lon - longitude)
            a = (
                math.sin(dlat / 2.0) ** 2
                + math.cos(lat1_rad) * math.cos(math.radians(h_lat)) * math.sin(dlon / 2.0) ** 2
            )
            dist_to_hotspot = EARTH_RADIUS_KM * 2.0 * math.asin(min(1.0, math.sqrt(a)))

            # If user search radius overlaps cluster boundary
            if dist_to_hotspot <= (radius_km + h_rad_km):
                nearby_hotspots_count += 1
    except Exception as e:
        nearby_hotspots_count = 0

    # Format return records with distance_km attached
    records_output = []
    for dist, rec in matched_records[:limit]:
        rec_dict = {
            "crime_id": rec.crime_id,
            "timestamp": rec.timestamp,
            "date": rec.date,
            "time": rec.time,
            "year": rec.year,
            "month": rec.month,
            "day_of_week": rec.day_of_week,
            "hour": rec.hour,
            "crime_type": rec.crime_type,
            "ipc_bns_section": rec.ipc_bns_section,
            "severity_score": rec.severity_score,
            "district": rec.district,
            "police_station": rec.police_station,
            "location_name": rec.location_name,
            "location_type": rec.location_type,
            "latitude": rec.latitude,
            "longitude": rec.longitude,
            "weapon_used": rec.weapon_used,
            "investigation_status": rec.investigation_status,
            "created_at": rec.created_at,
            "distance_km": round(dist, 3)
        }
        records_output.append(rec_dict)

    return {
        "query_latitude": latitude,
        "query_longitude": longitude,
        "radius_km": radius_km,
        "total_crimes_nearby": total_matched,
        "average_severity": avg_sev,
        "most_common_crime_type": most_common,
        "high_severity_crimes": high_sev,
        "high_severity_percentage": high_sev_pct,
        "crime_type_breakdown": breakdown,
        "severity_distribution": sev_dist,
        "nearby_hotspots_count": nearby_hotspots_count,
        "records": records_output
    }


def get_crime_density(
    db: Session,
    district: Optional[str] = None,
    crime_type: Optional[str] = None,
    year: Optional[int] = None,
    sample_size: int = 5000
) -> Dict[str, Any]:
    """
    Returns actual coordinate triples [lat, lon, weight] for heatmap visualization.
    Real data only from SQLite database.
    """
    query = db.query(CrimeRecord.latitude, CrimeRecord.longitude, CrimeRecord.severity_score)
    if district and district != "All Districts":
        query = query.filter(CrimeRecord.district.ilike(f"%{district}%"))
    if crime_type and crime_type != "All Crime Types":
        query = query.filter(CrimeRecord.crime_type.ilike(f"%{crime_type}%"))
    if year:
        query = query.filter(CrimeRecord.year == year)

    rows = query.all()
    total = len(rows)

    if total > sample_size:
        step = max(1, total // sample_size)
        sampled = rows[::step][:sample_size]
    else:
        sampled = rows

    points = [[round(r[0], 5), round(r[1], 5), round(r[2] / 5.0, 2)] for r in sampled]
    return {
        "total_points": len(points),
        "points": points
    }
