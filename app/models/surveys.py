from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class SurveyStatus(str, enum.Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class SurveyRecord(Base):
    __tablename__ = "survey_records"

    id = Column(Integer, primary_key=True, index=True)
    survey_number = Column(String(50), nullable=False, index=True) # e.g. "SURV-2025-50/1"
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    surveyor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    status = Column(Enum(SurveyStatus), default=SurveyStatus.IN_PROGRESS, nullable=False, index=True)
    survey_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    submission_date = Column(DateTime, nullable=True)
    verification_date = Column(DateTime, nullable=True)
    
    old_area_hectares = Column(Float, nullable=False)
    new_area_hectares = Column(Float, nullable=False)
    area_diff_hectares = Column(Float, default=0.0)
    area_diff_percent = Column(Float, default=0.0)
    
    gps_accuracy_meters = Column(Float, default=0.5)
    surveyor_remarks = Column(Text, nullable=True)
    verification_remarks = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parcel = relationship("LandParcel", back_populates="surveys")
    surveyor = relationship("User", back_populates="surveys", foreign_keys=[surveyor_id])
    verifier = relationship("User", back_populates="verified_surveys", foreign_keys=[verified_by_id])
    points = relationship("SurveyPoint", back_populates="survey", cascade="all, delete-orphan", order_by="SurveyPoint.point_order")
    boundaries = relationship("ParcelBoundary", back_populates="survey", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="survey", cascade="all, delete-orphan")

class SurveyPoint(Base):
    __tablename__ = "survey_points"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("survey_records.id"), nullable=False, index=True)
    point_order = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.5)
    point_type = Column(String(50), default="Boundary Corner")  # Corner, GPS Reference, Benchmark, Tree, Bund
    remarks = Column(String(255), nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow)

    survey = relationship("SurveyRecord", back_populates="points")

class ParcelBoundary(Base):
    __tablename__ = "parcel_boundaries"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("survey_records.id"), nullable=False, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    boundary_type = Column(String(30), default="NEW")  # "OLD" or "NEW"
    geojson_polygon = Column(Text, nullable=False)
    calculated_area_ha = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    survey = relationship("SurveyRecord", back_populates="boundaries")
