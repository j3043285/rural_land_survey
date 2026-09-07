from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class BoundaryStatus(str, enum.Enum):
    VERIFIED = "Verified"
    IN_PROGRESS = "In Progress"
    DISCREPANCY = "Discrepancy"
    PENDING = "Pending"

class LandType(str, enum.Enum):
    AGRICULTURAL_KHARIF = "Agricultural (Kharif)"
    AGRICULTURAL_RABI = "Agricultural (Rabi)"
    HORTICULTURE = "Horticulture"
    FOREST = "Forest"
    BARREN = "Barren"
    OTHER = "Others"

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, index=True)
    aadhaar_masked = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ownerships = relationship("ParcelOwner", back_populates="farmer")
    documents = relationship("Document", back_populates="farmer")

class LandParcel(Base):
    __tablename__ = "land_parcels"

    id = Column(Integer, primary_key=True, index=True)
    survey_number = Column(String(50), nullable=False, index=True)
    gat_number = Column(String(50), nullable=False, index=True)
    khata_number = Column(String(50), nullable=False, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    
    # Area measurements
    area_hectares = Column(Float, nullable=False)
    area_acres = Column(Float, nullable=False)
    
    # Types & Statuses
    land_type = Column(String(60), default=LandType.AGRICULTURAL_KHARIF.value, nullable=False)
    boundary_status = Column(Enum(BoundaryStatus), default=BoundaryStatus.PENDING, nullable=False, index=True)
    discrepancy_status = Column(String(50), default="No Discrepancy")  # "No Discrepancy" or "Discrepancy Found"
    
    # Primary coordinates
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    
    # Boundary GeoJSON representations
    boundary_geojson = Column(Text, nullable=False)  # GeoJSON polygon coordinates
    old_boundary_geojson = Column(Text, nullable=True) # Historical / 7-12 record boundary
    
    remarks = Column(String(255), default="Boundary matched with GPS")
    last_survey_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    village = relationship("Village", back_populates="parcels")
    owners = relationship("ParcelOwner", back_populates="parcel", cascade="all, delete-orphan")
    surveys = relationship("SurveyRecord", back_populates="parcel", cascade="all, delete-orphan")
    discrepancies = relationship("Discrepancy", back_populates="parcel", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="parcel", cascade="all, delete-orphan")
    crops = relationship("CropRecord", back_populates="parcel", cascade="all, delete-orphan")
    mutations = relationship("MutationRecord", back_populates="parcel", cascade="all, delete-orphan")
    grievances = relationship("Grievance", back_populates="parcel", cascade="all, delete-orphan")

class ParcelOwner(Base):
    __tablename__ = "parcel_owners"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    ownership_share = Column(Float, default=1.0)  # Fraction e.g. 1.0 = 100%, 0.5 = 50%
    is_primary = Column(Integer, default=1)  # 1 if primary owner name displayed on 7/12

    parcel = relationship("LandParcel", back_populates="owners")
    farmer = relationship("Farmer", back_populates="ownerships")

class CropRecord(Base):
    __tablename__ = "crop_records"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    season = Column(String(30), nullable=False)  # Kharif / Rabi / Summer
    year = Column(Integer, nullable=False)
    crop_name = Column(String(100), nullable=False)
    area_covered = Column(Float, nullable=False)  # in hectares
    irrigation_source = Column(String(60), default="Well / Rainfed")

    parcel = relationship("LandParcel", back_populates="crops")

class MutationRecord(Base):
    __tablename__ = "mutation_records"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    ferfar_number = Column(String(50), nullable=False, index=True)
    mutation_date = Column(DateTime, nullable=False)
    mutation_type = Column(String(100), nullable=False) # Inherited / Sale / Partition / Mortgage
    details = Column(Text, nullable=False)
    approved_by = Column(String(100), default="Talathi / Circle Officer")
    status = Column(String(30), default="Certified")

    parcel = relationship("LandParcel", back_populates="mutations")
