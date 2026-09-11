"""
Rakshak.ai - Temporal Crime Pattern Analysis Service
====================================================

This service provides aggregated spatiotemporal analysis across Delhi crime incidents.
It evaluates longitudinal trends, circadian rhythms, day-of-week distributions, and
seasonal variations to identify high-risk temporal windows for proactive law enforcement.

Calculations:
-------------
- Hourly distribution across all 24 hours (00:00 - 23:00)
- Day of week distribution ordered chronologically (Monday - Sunday)
- Monthly distribution (January - December)
- Annual distribution across historical years (2015 - 2025)
- Category breakdown across crime types
- Spatial breakdown across Delhi police districts
- Peak indicators: peak hour, peak day, peak month, peak year
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models import CrimeRecord

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _apply_filters(query, district: Optional[str] = None, crime_type: Optional[str] = None, year: Optional[int] = None):
    """
    Applies optional query filters for district, crime_type, and year.
    """
    if district:
        query = query.filter(CrimeRecord.district.ilike(f"%{district}%"))
    if crime_type:
        query = query.filter(CrimeRecord.crime_type.ilike(f"%{crime_type}%"))
    if year:
        query = query.filter(CrimeRecord.year == year)
    return query


def get_temporal_summary(
    db: Session,
    district: Optional[str] = None,
    crime_type: Optional[str] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Computes major temporal peaks (peak hour, day, month, year) with key insights.
    """
    base_query = _apply_filters(db.query(CrimeRecord), district, crime_type, year)
    total_crimes = base_query.count()

    if total_crimes == 0:
        return {
            "total_crimes_analyzed": 0,
            "filters_applied": {"district": district, "crime_type": crime_type, "year": year},
            "peak_hour": {"value": None, "label": "N/A", "count": 0, "percentage": 0.0},
            "peak_day": {"value": None, "label": "N/A", "count": 0, "percentage": 0.0},
            "peak_month": {"value": None, "label": "N/A", "count": 0, "percentage": 0.0},
            "peak_year": {"value": None, "label": "N/A", "count": 0, "percentage": 0.0},
            "key_insights": ["No crime records match the specified filter criteria."]
        }

    # 1. Peak Hour
    hour_query = _apply_filters(
        db.query(CrimeRecord.hour, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.hour).order_by(desc("cnt")).first()
    
    peak_hour_val = hour_query[0] if hour_query else 0
    peak_hour_cnt = hour_query[1] if hour_query else 0
    peak_hour_pct = round((peak_hour_cnt / total_crimes) * 100, 2)
    peak_hour_label = f"{peak_hour_val:02d}:00 - {(peak_hour_val + 1) % 24:02d}:00"

    # 2. Peak Day
    day_query = _apply_filters(
        db.query(CrimeRecord.day_of_week, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.day_of_week).order_by(desc("cnt")).first()

    peak_day_val = day_query[0] if day_query else "N/A"
    peak_day_cnt = day_query[1] if day_query else 0
    peak_day_pct = round((peak_day_cnt / total_crimes) * 100, 2)

    # 3. Peak Month
    month_query = _apply_filters(
        db.query(CrimeRecord.month, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.month).order_by(desc("cnt")).first()

    peak_month_val = month_query[0] if month_query else 1
    peak_month_cnt = month_query[1] if month_query else 0
    peak_month_pct = round((peak_month_cnt / total_crimes) * 100, 2)
    peak_month_label = MONTH_NAMES.get(peak_month_val, f"Month {peak_month_val}")

    # 4. Peak Year
    year_query = _apply_filters(
        db.query(CrimeRecord.year, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.year).order_by(desc("cnt")).first()

    peak_year_val = year_query[0] if year_query else 2025
    peak_year_cnt = year_query[1] if year_query else 0
    peak_year_pct = round((peak_year_cnt / total_crimes) * 100, 2)

    # Key analytical takeaways
    insights = [
        f"Peak crime volume occurs at {peak_hour_label} with {peak_hour_cnt:,} incidents ({peak_hour_pct}% of total).",
        f"The highest crime day is {peak_day_val} accounting for {peak_day_cnt:,} recorded crimes ({peak_day_pct}%).",
        f"Seasonal surge peaks in {peak_month_label} with {peak_month_cnt:,} incidents ({peak_month_pct}%).",
        f"Peak annual volume recorded in {peak_year_val} with {peak_year_cnt:,} crimes ({peak_year_pct}%)."
    ]

    return {
        "total_crimes_analyzed": total_crimes,
        "filters_applied": {
            "district": district,
            "crime_type": crime_type,
            "year": year
        },
        "peak_hour": {
            "value": peak_hour_val,
            "label": peak_hour_label,
            "count": peak_hour_cnt,
            "percentage": peak_hour_pct
        },
        "peak_day": {
            "value": peak_day_val,
            "label": peak_day_val,
            "count": peak_day_cnt,
            "percentage": peak_day_pct
        },
        "peak_month": {
            "value": peak_month_val,
            "label": peak_month_label,
            "count": peak_month_cnt,
            "percentage": peak_month_pct
        },
        "peak_year": {
            "value": peak_year_val,
            "label": str(peak_year_val),
            "count": peak_year_cnt,
            "percentage": peak_year_pct
        },
        "key_insights": insights
    }


def get_full_temporal_analysis(
    db: Session,
    district: Optional[str] = None,
    crime_type: Optional[str] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Computes full temporal distributions (hourly, daily, monthly, yearly, crime types, districts)
    along with peak summaries, structured specifically for frontend charting.
    """
    summary = get_temporal_summary(db, district, crime_type, year)
    total_crimes = summary["total_crimes_analyzed"]

    if total_crimes == 0:
        return {
            "total_crimes_analyzed": 0,
            "filters_applied": summary["filters_applied"],
            "summary": summary,
            "hourly_distribution": [],
            "day_of_week_distribution": [],
            "monthly_distribution": [],
            "yearly_distribution": [],
            "crime_type_distribution": [],
            "district_distribution": []
        }

    # 1. Hourly Distribution (0 to 23 guaranteed)
    raw_hourly = dict(
        _apply_filters(
            db.query(CrimeRecord.hour, func.count(CrimeRecord.crime_id)),
            district, crime_type, year
        ).group_by(CrimeRecord.hour).all()
    )
    hourly_dist = [
        {
            "hour": h,
            "label": f"{h:02d}:00",
            "count": raw_hourly.get(h, 0),
            "percentage": round((raw_hourly.get(h, 0) / total_crimes) * 100, 2)
        }
        for h in range(24)
    ]

    # 2. Day of Week Distribution (Chronological Monday -> Sunday)
    raw_daily = dict(
        _apply_filters(
            db.query(CrimeRecord.day_of_week, func.count(CrimeRecord.crime_id)),
            district, crime_type, year
        ).group_by(CrimeRecord.day_of_week).all()
    )
    daily_dist = [
        {
            "day": d,
            "count": raw_daily.get(d, 0),
            "percentage": round((raw_daily.get(d, 0) / total_crimes) * 100, 2)
        }
        for d in DAYS_ORDER
    ]

    # 3. Monthly Distribution (1 to 12)
    raw_monthly = dict(
        _apply_filters(
            db.query(CrimeRecord.month, func.count(CrimeRecord.crime_id)),
            district, crime_type, year
        ).group_by(CrimeRecord.month).all()
    )
    monthly_dist = [
        {
            "month": m,
            "month_name": MONTH_NAMES[m],
            "count": raw_monthly.get(m, 0),
            "percentage": round((raw_monthly.get(m, 0) / total_crimes) * 100, 2)
        }
        for m in range(1, 13)
    ]

    # 4. Yearly Distribution (Sorted chronologically)
    raw_yearly = _apply_filters(
        db.query(CrimeRecord.year, func.count(CrimeRecord.crime_id)),
        district, crime_type, year
    ).group_by(CrimeRecord.year).order_by(CrimeRecord.year).all()

    yearly_dist = [
        {
            "year": y,
            "count": cnt,
            "percentage": round((cnt / total_crimes) * 100, 2)
        }
        for y, cnt in raw_yearly
    ]

    # 5. Crime Type Distribution (Sorted descending by count)
    raw_types = _apply_filters(
        db.query(CrimeRecord.crime_type, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.crime_type).order_by(desc("cnt")).all()

    types_dist = [
        {
            "crime_type": ct,
            "count": cnt,
            "percentage": round((cnt / total_crimes) * 100, 2)
        }
        for ct, cnt in raw_types
    ]

    # 6. District Distribution (Sorted descending by count)
    raw_districts = _apply_filters(
        db.query(CrimeRecord.district, func.count(CrimeRecord.crime_id).label("cnt")),
        district, crime_type, year
    ).group_by(CrimeRecord.district).order_by(desc("cnt")).all()

    districts_dist = [
        {
            "district": dist,
            "count": cnt,
            "percentage": round((cnt / total_crimes) * 100, 2)
        }
        for dist, cnt in raw_districts
    ]

    return {
        "total_crimes_analyzed": total_crimes,
        "filters_applied": summary["filters_applied"],
        "summary": summary,
        "hourly_distribution": hourly_dist,
        "day_of_week_distribution": daily_dist,
        "monthly_distribution": monthly_dist,
        "yearly_distribution": yearly_dist,
        "crime_type_distribution": types_dist,
        "district_distribution": districts_dist
    }
