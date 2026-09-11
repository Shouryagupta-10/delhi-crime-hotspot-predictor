from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict



class CrimeRecordBase(BaseModel):
    """
    Base schema shared across creation and read operations.
    """
    timestamp: str = Field(..., description="Timestamp in YYYY-MM-DD HH:MM:SS format", example="2024-05-15 22:30:00")
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2024-05-15")
    time: str = Field(..., description="Time in HH:MM format", example="22:30")
    year: int = Field(..., ge=2000, le=2100, example=2024)
    month: int = Field(..., ge=1, le=12, example=5)
    day_of_week: str = Field(..., example="Wednesday")
    hour: int = Field(..., ge=0, le=23, example=22)
    crime_type: str = Field(..., example="Motor Vehicle Theft")
    ipc_bns_section: Optional[str] = Field(None, example="BNS Sec 303(2)")
    severity_score: int = Field(..., ge=1, le=5, example=3)
    district: str = Field(..., example="Central")
    police_station: str = Field(..., example="Paharganj")
    location_name: Optional[str] = Field(None, example="New Delhi Railway Station / Paharganj")
    location_type: Optional[str] = Field(None, example="Transit Hub / Commercial")
    latitude: float = Field(..., ge=28.0, le=29.5, description="Delhi latitude boundary", example=28.6432)
    longitude: float = Field(..., ge=76.5, le=77.8, description="Delhi longitude boundary", example=77.2140)
    weapon_used: Optional[str] = Field("No", example="No")
    investigation_status: Optional[str] = Field(None, example="Under Investigation")


class CrimeRecordCreate(CrimeRecordBase):
    """
    Schema for creating a new incident. Crime ID will be auto-generated if omitted.
    """
    crime_id: Optional[str] = Field(None, description="Optional custom Crime ID (auto-generated if omitted)")


class CrimeRecordResponse(CrimeRecordBase):
    """
    Schema returned for crime incident details.
    """
    crime_id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedCrimeResponse(BaseModel):
    """
    Envelope for paginated crime queries.
    """
    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: List[CrimeRecordResponse]


class CrimeFilterParams(BaseModel):
    """
    Internal schema for filtering crime queries.
    """
    district: Optional[str] = None
    crime_type: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    min_severity: Optional[int] = None
    police_station: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class DistrictCrimeCount(BaseModel):
    district: str
    count: int


class CrimeTypeCount(BaseModel):
    crime_type: str
    count: int


class StatsSummaryResponse(BaseModel):
    """
    Aggregated statistical breakdown of crime incidents.
    """
    total_crimes: int
    high_severity_crimes: int
    districts_count: int
    top_districts: List[DistrictCrimeCount]
    top_crime_types: List[CrimeTypeCount]


class HealthCheckResponse(BaseModel):
    """
    System diagnostic health response.
    """
    status: str
    app_name: str
    version: str
    database: str
    total_records_in_db: int


class HotspotTopCrime(BaseModel):
    type: str
    count: int


class HotspotCluster(BaseModel):
    """
    Individual spatial cluster representing a recurring crime hotspot.
    """
    cluster_id: int = Field(..., description="Unique integer ID of the cluster (0, 1, 2, ...)")
    crime_count: int = Field(..., description="Number of crime incidents assigned to this cluster")
    center_latitude: float = Field(..., description="Mean latitude centroid of the hotspot")
    center_longitude: float = Field(..., description="Mean longitude centroid of the hotspot")
    percentage_of_clustered_crimes: float = Field(..., description="Percentage of all clustered crimes in this hotspot")
    percentage_of_total_crimes: float = Field(..., description="Percentage of all analyzed crimes in this hotspot")
    primary_district: Optional[str] = Field(None, description="Dominant administrative district for this hotspot")
    avg_severity: Optional[float] = Field(None, description="Average crime severity score (1-5) in this hotspot")
    radius_meters: Optional[float] = Field(None, description="Estimated spatial radius in meters from the cluster centroid")
    top_crime_types: Optional[List[HotspotTopCrime]] = Field(None, description="Top crime categories occurring in this hotspot")


class HotspotParams(BaseModel):
    eps_km: float = Field(..., description="Epsilon neighborhood distance in kilometers")
    eps_radians: float = Field(..., description="Epsilon converted to spherical radians")
    min_samples: int = Field(..., description="Minimum points required to form a dense core cluster")
    distance_metric: str = Field(..., description="Geographical metric used (haversine with BallTree)")


class HotspotResponse(BaseModel):
    """
    Comprehensive DBSCAN geospatial hotspot detection response.
    """
    algorithm: str = Field(..., description="Algorithm name and clustering family")
    distance_metric_explanation: str = Field(..., description="Explanation of Haversine spherical distance metric")
    parameters: HotspotParams
    total_points_analyzed: int = Field(..., description="Total crime incidents analyzed")
    total_clusters_detected: int = Field(..., description="Total dense hotspot clusters identified")
    clustered_points_count: int = Field(..., description="Number of points belonging to hotspot clusters")
    noise_points_count: int = Field(..., description="Number of isolated crime incidents classified as noise (-1)")
    noise_percentage: float = Field(..., description="Percentage of incidents classified as noise")
    execution_time_seconds: float = Field(..., description="Computation time in seconds")
    hotspots: List[HotspotCluster] = Field(..., description="List of detected hotspots sorted by crime count descending")


class HourlyDistributionItem(BaseModel):
    hour: int = Field(..., description="Hour of day (0-23)")
    label: str = Field(..., description="Formatted time label (e.g. '20:00')")
    count: int = Field(..., description="Number of crimes recorded at this hour")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class DayOfWeekDistributionItem(BaseModel):
    day: str = Field(..., description="Day name (Monday - Sunday)")
    count: int = Field(..., description="Number of crimes recorded on this day")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class MonthlyDistributionItem(BaseModel):
    month: int = Field(..., description="Month number (1-12)")
    month_name: str = Field(..., description="Month name (January - December)")
    count: int = Field(..., description="Number of crimes recorded in this month")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class YearlyDistributionItem(BaseModel):
    year: int = Field(..., description="Year (2015-2025)")
    count: int = Field(..., description="Number of crimes recorded in this year")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class CrimeTypeDistributionItem(BaseModel):
    crime_type: str = Field(..., description="Category of offense")
    count: int = Field(..., description="Number of recorded incidents")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class DistrictDistributionItem(BaseModel):
    district: str = Field(..., description="Delhi Police District")
    count: int = Field(..., description="Number of recorded incidents")
    percentage: float = Field(..., description="Percentage of total filtered crimes")


class PeakMetric(BaseModel):
    value: Optional[Any] = Field(None, description="Peak value identifier (hour, day, month, or year)")
    label: str = Field(..., description="Human-readable peak label")
    count: int = Field(..., description="Number of crime incidents during peak window")
    percentage: float = Field(..., description="Proportion of total crimes occurring during peak window")


class TemporalSummaryResponse(BaseModel):
    """
    Summary of primary temporal peaks and analytical insights.
    """
    total_crimes_analyzed: int = Field(..., description="Total crime records analyzed")
    filters_applied: Dict[str, Any] = Field(..., description="Active filters (district, crime_type, year)")
    peak_hour: PeakMetric = Field(..., description="Hour with the highest crime concentration")
    peak_day: PeakMetric = Field(..., description="Day of week with the highest crime concentration")
    peak_month: PeakMetric = Field(..., description="Month with the highest crime concentration")
    peak_year: PeakMetric = Field(..., description="Year with the highest crime concentration")
    key_insights: List[str] = Field(..., description="Key analytical takeaways")


class TemporalAnalysisResponse(BaseModel):
    """
    Comprehensive temporal crime pattern dataset structured for charting.
    """
    total_crimes_analyzed: int = Field(..., description="Total crime records analyzed")
    filters_applied: Dict[str, Any] = Field(..., description="Active filters (district, crime_type, year)")
    summary: TemporalSummaryResponse = Field(..., description="High-level peak findings and insights")
    hourly_distribution: List[HourlyDistributionItem] = Field(..., description="24-hour circadian breakdown (0-23)")
    day_of_week_distribution: List[DayOfWeekDistributionItem] = Field(..., description="Chronological day-of-week breakdown (Mon-Sun)")
    monthly_distribution: List[MonthlyDistributionItem] = Field(..., description="Seasonal monthly breakdown (Jan-Dec)")
    yearly_distribution: List[YearlyDistributionItem] = Field(..., description="Annual longitudinal trend (2015-2025)")
    crime_type_distribution: List[CrimeTypeDistributionItem] = Field(..., description="Crime categories sorted descending by frequency")
    district_distribution: List[DistrictDistributionItem] = Field(..., description="Administrative districts sorted descending by frequency")


class RiskPredictionRequest(BaseModel):
    """
    Input parameters for evaluating historical crime risk at a spatio-temporal coordinate.
    """
    latitude: float = Field(..., ge=28.0, le=29.5, description="Geospatial latitude in Delhi", example=28.6432)
    longitude: float = Field(..., ge=76.5, le=77.8, description="Geospatial longitude in Delhi", example=77.2140)
    hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)", example=22)
    day: Optional[str] = Field(None, description="Day of the week (e.g. 'Friday')", example="Friday")
    day_of_week: Optional[str] = Field(None, description="Alternative alias for day of the week", example="Friday")
    month: int = Field(..., ge=1, le=12, description="Month of the year (1-12)", example=8)
    year: int = Field(..., ge=2000, le=2100, description="Incident year", example=2025)
    district: Optional[str] = Field(None, description="Optional Delhi police district", example="Central")
    crime_type: Optional[str] = Field(None, description="Optional specific crime category to evaluate", example="Robbery")


class RiskPredictionResponse(BaseModel):
    """
    Response payload for historical pattern crime-risk classification.
    """
    risk_level: str = Field(..., description="Predicted risk class: LOW, MEDIUM, or HIGH")
    risk_score: float = Field(..., description="Calibrated risk index from 0.0 to 100.0")
    confidence: float = Field(..., description="Model confidence score for the predicted class (0.0 to 1.0)")
    probabilities: Dict[str, float] = Field(..., description="Softmax probability distribution across LOW, MEDIUM, HIGH")
    input_parameters: Dict[str, Any] = Field(..., description="Validated inputs used for inference")
    explanation: str = Field(..., description="Transparent factor breakdown explaining the assigned risk")
    inference_time_ms: float = Field(..., description="Inference execution latency in milliseconds")
    model_info: Dict[str, Any] = Field(..., description="Metadata describing the model version and algorithm")


class ModelInfoResponse(BaseModel):
    """
    Information schema for XGBoost model status, features, and legitimate evaluation metrics.
    """
    model_name: str = Field(..., description="Descriptive model identifier")
    model_type: str = Field(..., description="Model architecture type")
    algorithm: str = Field(..., description="Underlying algorithm implementation")
    training_record_count: int = Field(..., description="Number of historical training records used")
    training_test_split: str = Field(..., description="Dataset splitting ratio")
    feature_list: List[str] = Field(..., description="Feature names input to the classifier")
    risk_classes: List[str] = Field(..., description="Target risk classification categories")
    training_methodology: str = Field(..., description="Explanation of ground-truth label formulation and validation")
    evaluation_metrics: Dict[str, Any] = Field(..., description="Legitimate metrics computed on holdout test set")
    training_time_seconds: float = Field(..., description="Time taken to train the model in seconds")
    model_status: str = Field(..., description="Current operational status of the model")


class NearbyCrimeRecord(CrimeRecordResponse):
    distance_km: float = Field(..., description="Geodesic distance from search coordinates in kilometers")


class NearbyCrimeTypeStat(BaseModel):
    crime_type: str
    count: int
    percentage: float


class NearbyCrimesResponse(BaseModel):
    """
    Response schema for geographic radius crime query around user's location.
    """
    query_latitude: float = Field(..., description="Query center latitude")
    query_longitude: float = Field(..., description="Query center longitude")
    radius_km: float = Field(..., description="Search perimeter in kilometers")
    total_crimes_nearby: int = Field(..., description="Total verified incidents within the radius")
    average_severity: float = Field(..., description="Mean severity score of nearby incidents (1-5)")
    most_common_crime_type: Optional[str] = Field(None, description="Dominant crime category in the area")
    high_severity_crimes: int = Field(0, description="Count of severe crimes (severity >= 4)")
    high_severity_percentage: float = Field(0.0, description="Percentage of nearby crimes that are high severity")
    crime_type_breakdown: List[NearbyCrimeTypeStat] = Field(default_factory=list, description="Categorical breakdown sorted descending")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="Incidents count per severity level (1-5)")
    nearby_hotspots_count: int = Field(0, description="Number of detected DBSCAN dense clusters overlapping this area")
    records: List[NearbyCrimeRecord] = Field(default_factory=list, description="Individual incident records sorted by distance ascending")


class CrimeDensityResponse(BaseModel):
    """
    Coordinates and intensities for real crime density heatmap visualization.
    """
    total_points: int = Field(..., description="Count of spatial coordinates returned")
    points: List[List[float]] = Field(..., description="List of [latitude, longitude, normalized_weight] tuples")



