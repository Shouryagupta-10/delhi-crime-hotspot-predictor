from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, init_db, SessionLocal
from models import CrimeRecord
from schemas import (
    CrimeRecordResponse,
    CrimeRecordCreate,
    PaginatedCrimeResponse,
    CrimeFilterParams,
    StatsSummaryResponse,
    HealthCheckResponse,
    HotspotResponse,
    TemporalAnalysisResponse,
    TemporalSummaryResponse,
    RiskPredictionRequest,
    RiskPredictionResponse,
    ModelInfoResponse,
    NearbyCrimesResponse,
    CrimeDensityResponse
)
from services import crime_service, hotspot, temporal, predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Initializes database tables and trains the XGBoost risk classifier on startup.
    """
    print("[*] Starting Rakshak.ai Backend...")
    init_db()
    db = SessionLocal()
    try:
        predictor.predictor_service.train_model(db)
    except Exception as exc:
        print(f"[!] Warning: Auto-training XGBoost on startup encountered: {exc}")
    finally:
        db.close()
    yield
    print("[*] Shutting down Rakshak.ai Backend...")



app = FastAPI(
    title="Rakshak.ai - Crime Hotspot Detector API",
    description=(
        "Backend API foundation for Rakshak.ai: Crime Hotspot Detection & Risk Forecasting for Delhi. "
        "Built with FastAPI, SQLite, SQLAlchemy, Pandas, GeoPandas, Scikit-learn, and XGBoost."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to support future frontend dashboards (React, Vite, Leaflet, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def root():
    """
    Root endpoint for API service discovery.
    """
    return {
        "app": "Rakshak.ai",
        "description": "Delhi Crime Hotspot Detector API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check diagnostic confirming API & SQLite database availability.
    """
    try:
        total_records = db.query(func.count(CrimeRecord.crime_id)).scalar() or 0
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {str(exc)}"
        total_records = -1

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        app_name="Rakshak.ai",
        version="1.0.0",
        database=db_status,
        total_records_in_db=total_records
    )


@app.get("/api/crimes", response_model=PaginatedCrimeResponse, tags=["Crime Records"])
def list_crimes(
    district: Optional[str] = Query(None, description="Filter by Delhi Police District (e.g. Central, North, South)"),
    crime_type: Optional[str] = Query(None, description="Filter by crime category (e.g. Motor Vehicle Theft, Snatching)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year (2015-2025)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    min_severity: Optional[int] = Query(None, ge=1, le=5, description="Filter by minimum severity (1 to 5)"),
    police_station: Optional[str] = Query(None, description="Filter by police station name"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Records per page"),
    db: Session = Depends(get_db)
):
    """
    Query historical crime records with multidimensional filtering and pagination.
    """
    filters = CrimeFilterParams(
        district=district,
        crime_type=crime_type,
        year=year,
        month=month,
        min_severity=min_severity,
        police_station=police_station,
        start_date=start_date,
        end_date=end_date
    )
    return crime_service.get_crimes(db=db, filters=filters, page=page, page_size=page_size)


@app.get("/api/crimes/stats/summary", response_model=StatsSummaryResponse, tags=["Analytics"])
def get_crime_stats(db: Session = Depends(get_db)):
    """
    Fetch aggregated summary statistics across districts and crime categories.
    """
    return crime_service.get_crime_summary_stats(db=db)


@app.get("/api/crimes/nearby", response_model=NearbyCrimesResponse, tags=["Crime Records"])
def get_nearby_crimes(
    latitude: float = Query(..., ge=28.0, le=29.5, description="Search latitude in Delhi (e.g. 28.6315)"),
    longitude: float = Query(..., ge=76.5, le=77.8, description="Search longitude in Delhi (e.g. 77.2167)"),
    radius_km: float = Query(2.0, ge=0.1, le=20.0, description="Geographic radius in kilometers (default 2.0 km)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum nearby incidents to return"),
    db: Session = Depends(get_db)
):
    """
    Find crime incidents within a specified radius (km) from coordinates using the Haversine spherical distance metric.
    Calculates detailed nearby crime statistics, severity breakdown, and overlaps with detected DBSCAN hotspots.
    """
    return crime_service.get_nearby_crimes(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )


@app.get("/api/crimes/density", response_model=CrimeDensityResponse, tags=["Analytics"])
def get_crime_density(
    district: Optional[str] = Query(None, description="Optional filter by Delhi Police District"),
    crime_type: Optional[str] = Query(None, description="Optional filter by crime category"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Optional filter by year"),
    sample_size: int = Query(5000, ge=10, le=10000, description="Number of coordinates for heatmap layer"),
    db: Session = Depends(get_db)
):
    """
    Return coordinate triples [latitude, longitude, intensity] for the real crime density heatmap layer.
    """
    return crime_service.get_crime_density(
        db=db,
        district=district,
        crime_type=crime_type,
        year=year,
        sample_size=sample_size
    )


# ============================================================================
# Temporal Crime Pattern Analysis
# ============================================================================
@app.get("/api/crimes/temporal", response_model=TemporalAnalysisResponse, tags=["Temporal Analysis"])
def get_temporal_crime_analysis(
    district: Optional[str] = Query(None, description="Optional filter by Delhi Police District"),
    crime_type: Optional[str] = Query(None, description="Optional filter by crime category"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Optional filter by year"),
    db: Session = Depends(get_db)
):
    """
    Comprehensive temporal crime pattern analysis structured for charting:
    - 24-hour circadian distribution (00:00 - 23:00)
    - Chronological day-of-week breakdown (Monday - Sunday)
    - Seasonal monthly distribution (January - December)
    - Longitudinal annual trend (2015 - 2025)
    - Offense categories and administrative district distributions
    - Peak temporal indicators (peak hour, day, month, year)
    """
    return temporal.get_full_temporal_analysis(
        db=db,
        district=district,
        crime_type=crime_type,
        year=year
    )


@app.get("/api/crimes/temporal/summary", response_model=TemporalSummaryResponse, tags=["Temporal Analysis"])
def get_temporal_crime_summary(
    district: Optional[str] = Query(None, description="Optional filter by Delhi Police District"),
    crime_type: Optional[str] = Query(None, description="Optional filter by crime category"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Optional filter by year"),
    db: Session = Depends(get_db)
):
    """
    High-level temporal findings reporting peak crime hour, peak day,
    peak month, peak year, and actionable analytical insights.
    """
    return temporal.get_temporal_summary(
        db=db,
        district=district,
        crime_type=crime_type,
        year=year
    )


@app.get("/api/crimes/{crime_id}", response_model=CrimeRecordResponse, tags=["Crime Records"])

def get_crime_details(crime_id: str, db: Session = Depends(get_db)):
    """
    Fetch details for a specific crime record by its Crime ID.
    """
    record = crime_service.get_crime_by_id(db=db, crime_id=crime_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crime incident with ID '{crime_id}' not found."
        )
    return record


@app.post("/api/crimes", response_model=CrimeRecordResponse, status_code=status.HTTP_201_CREATED, tags=["Crime Records"])
def log_crime_incident(crime_in: CrimeRecordCreate, db: Session = Depends(get_db)):
    """
    Log a new crime incident into the SQLite database.
    """
    return crime_service.create_crime_record(db=db, crime_in=crime_in)


# ============================================================================
# DBSCAN Spatial Hotspot Detection
# ============================================================================
@app.get("/api/hotspots", response_model=HotspotResponse, tags=["Hotspots (DBSCAN)"])
def get_spatial_hotspots(
    eps_km: float = Query(
        0.5,
        ge=0.05,
        le=10.0,
        description="Epsilon neighborhood radius in kilometers (e.g., 0.5 = 500 meters)"
    ),
    min_samples: int = Query(
        25,
        ge=2,
        le=5000,
        description="Minimum crime incidents required within eps_km to form a dense core cluster"
    ),
    district: Optional[str] = Query(None, description="Optional filter by Delhi Police District"),
    crime_type: Optional[str] = Query(None, description="Optional filter by crime category"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Optional filter by year"),
    min_severity: Optional[int] = Query(None, ge=1, le=5, description="Optional filter by minimum severity score"),
    db: Session = Depends(get_db)
):
    """
    Detect spatial crime hotspots across Delhi using DBSCAN clustering with the Haversine metric.

    - **eps_km**: Clustering neighborhood distance in kilometers. Converted to spherical radians using Earth radius (6371.0088 km).
    - **min_samples**: Density threshold. A point must have at least this many neighbors within eps_km to form a core hotspot.
    - **Noise Points (-1)**: Sporadic/isolated crimes that do not belong to dense hotspots are treated as noise.
    """
    return hotspot.detect_crime_hotspots(
        db=db,
        eps_km=eps_km,
        min_samples=min_samples,
        district=district,
        crime_type=crime_type,
        year=year,
        min_severity=min_severity
    )


# ============================================================================
# XGBoost Crime-Risk Classification
# ============================================================================
@app.post("/api/predict-risk", response_model=RiskPredictionResponse, tags=["Risk Prediction (XGBoost)"])
def predict_crime_risk(
    req: RiskPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Classify historical spatiotemporal crime risk into LOW, MEDIUM, or HIGH tiers.

    - **Inputs**: coordinates (lat, lon), hour (0-23), day of week, month (1-12), year, district, and optional crime type.
    - **Model**: Multi-class XGBoost classifier trained on historical Delhi incidents.
    - **Outputs**: Calibrated continuous risk score (0-100), categorical risk tier, class probabilities, and factor breakdown.
    - **Disclaimer**: Historical risk classification prototype; does NOT guarantee exact future events.
    """
    day_val = req.day or req.day_of_week or "Wednesday"
    return predictor.predictor_service.predict_risk(
        db=db,
        latitude=req.latitude,
        longitude=req.longitude,
        hour=req.hour,
        day=day_val,
        month=req.month,
        year=req.year,
        district=req.district,
        crime_type=req.crime_type
    )


@app.get("/api/model/info", response_model=ModelInfoResponse, tags=["Risk Prediction (XGBoost)"])
def get_model_information(db: Session = Depends(get_db)):
    """
    Retrieve architecture details, feature sets, risk classes, and legitimate holdout evaluation metrics
    for the XGBoost crime-risk classification model.
    """
    if not predictor.predictor_service.is_trained:
        predictor.predictor_service.train_model(db)
    return predictor.predictor_service.get_model_info()




