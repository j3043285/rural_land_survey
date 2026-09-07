from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    document_type = Column(String(60), nullable=False) # "7/12 Extract", "8A Khata", "Ferfar Patrak", "Drone Orthomosaic", "Ground Photo", "Survey Report"
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(150), nullable=False)
    file_size_kb = Column(Integer, default=0)
    mime_type = Column(String(50), default="application/pdf")
    
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=True, index=True)
    survey_id = Column(Integer, ForeignKey("survey_records.id"), nullable=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True, index=True)
    
    uploaded_by = Column(String(100), default="Surveyor")
    is_verified = Column(Boolean, default=False)
    ocr_extracted_text = Column(Text, nullable=True)
    ocr_parsed_data = Column(Text, nullable=True) # JSON string of parsed fields
    
    created_at = Column(DateTime, default=datetime.utcnow)

    parcel = relationship("LandParcel", back_populates="documents")
    survey = relationship("SurveyRecord", back_populates="documents")
    farmer = relationship("Farmer", back_populates="documents")
