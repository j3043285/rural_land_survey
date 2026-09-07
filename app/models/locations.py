from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    state = Column(String(100), default="Maharashtra", nullable=False)
    code = Column(String(20), nullable=True)
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)

    talukas = relationship("Taluka", back_populates="district", cascade="all, delete-orphan")

class Taluka(Base):
    __tablename__ = "talukas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)

    district = relationship("District", back_populates="talukas")
    villages = relationship("Village", back_populates="taluka", cascade="all, delete-orphan")

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=True)
    taluka_id = Column(Integer, ForeignKey("talukas.id"), nullable=False, index=True)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    boundary_geojson = Column(String, nullable=True)  # Village outline GeoJSON

    taluka = relationship("Taluka", back_populates="villages")
    parcels = relationship("LandParcel", back_populates="village", cascade="all, delete-orphan")
