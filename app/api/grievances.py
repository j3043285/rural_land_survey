from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.grievances import Grievance, GrievanceStatus
from app.models.parcels import LandParcel
from app.models.system import AuditLog, Notification
from app.models.users import User
from app.schemas.grievances import GrievanceCreate, GrievanceResponse, GrievanceUpdate

router = APIRouter(prefix="/grievances", tags=["Farmer Grievances"])


@router.get("", response_model=List[GrievanceResponse])
def get_grievances(
    status: Optional[GrievanceStatus] = Query(None),
    parcel_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Grievance).order_by(Grievance.created_at.desc())
    if status:
        query = query.filter(Grievance.status == status)
    if parcel_id:
        query = query.filter(Grievance.parcel_id == parcel_id)
    return query.all()


@router.post("", response_model=GrievanceResponse, status_code=201)
def create_grievance(grievance_in: GrievanceCreate, db: Session = Depends(get_db)):
    if grievance_in.parcel_id and not db.query(LandParcel).filter(LandParcel.id == grievance_in.parcel_id).first():
        raise HTTPException(status_code=404, detail="Land parcel not found")
    grievance = Grievance(
        ticket_number=f"GRV-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}",
        **grievance_in.model_dump(),
    )
    db.add(grievance)
    db.flush()
    db.add(Notification(
        title="New Farmer Grievance",
        message=f"Ticket {grievance.ticket_number} submitted by {grievance.farmer_name}.",
        notification_type="INFO",
        link="/grievances",
    ))
    db.commit()
    db.refresh(grievance)
    return grievance


@router.patch("/{id}", response_model=GrievanceResponse)
def update_grievance(
    id: int,
    grievance_in: GrievanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grievance = db.query(Grievance).filter(Grievance.id == id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    old_status = grievance.status.value
    for key, value in grievance_in.model_dump(exclude_unset=True).items():
        setattr(grievance, key, value)
    db.add(AuditLog(
        user_id=current_user.id,
        action="UPDATED_GRIEVANCE",
        entity_name="Grievance",
        entity_id=grievance.ticket_number,
        old_value=old_status,
        new_value=grievance.status.value,
    ))
    db.commit()
    db.refresh(grievance)
    return grievance