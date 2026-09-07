from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.system import Notification, AuditLog
from app.schemas.system import NotificationResponse, AuditLogResponse

router = APIRouter(prefix="/system", tags=["System, Notifications & Audit Logs"])

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()

@router.post("/notifications/{id}/read")
def mark_notification_read(id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"status": "ok"}

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = Query(50), db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()

@router.get("/status")
def get_system_status():
    return {
        "gps_status": "Connected",
        "gps_coordinates": {"lat": 19.0760, "lng": 72.8777, "text": "19.0760° N, 72.8777° E"},
        "last_sync": "12 Apr 2025, 14:32",
        "land_data_provider": settings.LAND_DATA_PROVIDER,
        "is_mock_data": settings.LAND_DATA_PROVIDER.lower() == "mock",
        "environment": "Demo / Evaluation",
        "project": "SIH 2026 - Problem Statement SIH26010",
        "active_satellite_constellation": "NavIC / GPS L1/L5 Dual Band",
        "rtk_accuracy": "± 0.45 meters"
    }
