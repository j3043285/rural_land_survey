from datetime import datetime, timedelta
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class GrievanceStatus(str, enum.Enum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    FIELD_VISIT_REQUIRED = "Field Visit Required"
    RESOLVED = "Resolved"
    REJECTED = "Rejected"


class GrievanceType(str, enum.Enum):
    BOUNDARY = "Boundary dispute"
    AREA = "Area mismatch"
    OWNERSHIP = "Ownership or mutation"
    RECORD = "Record correction"
    OTHER = "Other"


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(30), unique=True, nullable=False, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=True, index=True)
    farmer_name = Column(String(150), nullable=False)
    farmer_phone = Column(String(30), nullable=False)
    preferred_language = Column(String(20), default="Marathi", nullable=False)
    grievance_type = Column(Enum(GrievanceType), default=GrievanceType.OTHER, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(GrievanceStatus), default=GrievanceStatus.OPEN, nullable=False, index=True)
    assigned_officer = Column(String(150), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    due_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parcel = relationship("LandParcel", back_populates="grievances")