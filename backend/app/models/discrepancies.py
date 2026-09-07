from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class DiscrepancyType(str, enum.Enum):
    BOUNDARY_MISMATCH = "Boundary Mismatch"
    AREA_MISMATCH = "Area Mismatch"
    OVERLAPPING_PARCELS = "Overlapping Parcels"
    GAPS = "Gaps / Unclaimed Enclave"
    INVALID_GEOMETRY = "Invalid Geometry"
    DUPLICATE_PARCEL = "Duplicate Parcel"

class DiscrepancySeverity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class DiscrepancyStatus(str, enum.Enum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    RESOLVED = "Resolved"
    DISMISSED = "Dismissed"

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    survey_id = Column(Integer, ForeignKey("survey_records.id"), nullable=True, index=True)
    
    discrepancy_type = Column(Enum(DiscrepancyType), default=DiscrepancyType.BOUNDARY_MISMATCH, nullable=False)
    severity = Column(Enum(DiscrepancySeverity), default=DiscrepancySeverity.MEDIUM, nullable=False)
    status = Column(Enum(DiscrepancyStatus), default=DiscrepancyStatus.OPEN, nullable=False)
    
    old_geometry_geojson = Column(Text, nullable=True)
    new_geometry_geojson = Column(Text, nullable=True)
    difference_geometry_geojson = Column(Text, nullable=True) # The encroached / missing polygon slice
    
    old_area_ha = Column(Float, nullable=False)
    new_area_ha = Column(Float, nullable=False)
    diff_area_ha = Column(Float, nullable=False)
    diff_percent = Column(Float, nullable=False)
    
    assigned_officer = Column(String(100), default="Circle Inspector / Tahsildar")
    detected_date = Column(DateTime, default=datetime.utcnow)
    resolved_date = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    parcel = relationship("LandParcel", back_populates="discrepancies")
