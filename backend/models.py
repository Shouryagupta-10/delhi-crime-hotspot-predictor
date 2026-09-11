from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from database import Base


class CrimeRecord(Base):
    """
    SQLAlchemy ORM model representing Delhi historical and real-time crime incidents.
    Designed to store spatiotemporal data for hotspot analysis and risk modeling.
    """
    __tablename__ = "crime_records"

    crime_id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(String(32), nullable=False, index=True)  # Format: YYYY-MM-DD HH:MM:SS
    date = Column(String(16), nullable=False, index=True)        # Format: YYYY-MM-DD
    time = Column(String(8), nullable=False)                    # Format: HH:MM
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    day_of_week = Column(String(16), nullable=False, index=True)
    hour = Column(Integer, nullable=False, index=True)

    crime_type = Column(String(128), nullable=False, index=True)
    ipc_bns_section = Column(String(64), nullable=True)
    severity_score = Column(Integer, nullable=False, index=True)  # 1 (Minor) to 5 (Critical)

    district = Column(String(64), nullable=False, index=True)
    police_station = Column(String(128), nullable=False, index=True)
    location_name = Column(String(256), nullable=True)
    location_type = Column(String(128), nullable=True)

    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)

    weapon_used = Column(String(8), default="No")               # "Yes" or "No"
    investigation_status = Column(String(64), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Composite indexes for fast spatiotemporal clustering and dashboard filters
    __table_args__ = (
        Index("idx_crime_district_year", "district", "year"),
        Index("idx_crime_lat_lon", "latitude", "longitude"),
        Index("idx_crime_type_severity", "crime_type", "severity_score"),
    )

    def __repr__(self):
        return f"<CrimeRecord(crime_id='{self.crime_id}', type='{self.crime_type}', district='{self.district}')>"
