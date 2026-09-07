from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False) # e.g. "UPDATED_PARCEL_BOUNDARY", "VERIFIED_SURVEY"
    entity_name = Column(String(60), nullable=False) # "LandParcel", "SurveyRecord"
    entity_id = Column(String(60), nullable=False) # "50/1" or primary key
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(45), default="127.0.0.1")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO") # "INFO", "WARNING", "SUCCESS", "ERROR"
    is_read = Column(Boolean, default=False, index=True)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
