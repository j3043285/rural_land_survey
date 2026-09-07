from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.discrepancies import Discrepancy, DiscrepancyStatus
from app.models.parcels import LandParcel, BoundaryStatus
from app.models.system import AuditLog, Notification
from app.schemas.discrepancies import DiscrepancyResponse, DiscrepancyResolveRequest
from app.api.deps import get_current_user
from app.models.users import User

router = APIRouter(prefix="/discrepancies", tags=["Boundary Discrepancies"])

@router.get("", response_model=List[DiscrepancyResponse])
def get_discrepancies(
    status: Optional[str] = Query(None),
    village_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Discrepancy).join(Discrepancy.parcel)
    if status:
        q = q.filter(Discrepancy.status == status)
    if village_id:
        q = q.filter(LandParcel.village_id == village_id)
        
    discs = q.order_by(Discrepancy.detected_date.desc()).all()
    results = []
    for d in discs:
        p = d.parcel
        owner = p.owners[0].farmer.full_name if p and p.owners else "N/A"
        results.append({
            "id": d.id,
            "parcel_id": d.parcel_id,
            "survey_id": d.survey_id,
            "discrepancy_type": d.discrepancy_type,
            "severity": d.severity,
            "status": d.status,
            "old_geometry_geojson": d.old_geometry_geojson,
            "new_geometry_geojson": d.new_geometry_geojson,
            "difference_geometry_geojson": d.difference_geometry_geojson,
            "old_area_ha": d.old_area_ha,
            "new_area_ha": d.new_area_ha,
            "diff_area_ha": d.diff_area_ha,
            "diff_percent": d.diff_percent,
            "assigned_officer": d.assigned_officer,
            "detected_date": d.detected_date,
            "resolved_date": d.resolved_date,
            "resolution_notes": d.resolution_notes,
            "survey_number": p.survey_number if p else "",
            "gat_number": p.gat_number if p else "",
            "owner_name": owner,
            "village_name": p.village.name if p and p.village else ""
        })
    return results

@router.post("/{id}/resolve", response_model=DiscrepancyResponse)
def resolve_discrepancy(
    id: int, 
    res_in: DiscrepancyResolveRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
        
    disc.status = res_in.status
    disc.resolved_date = datetime.utcnow()
    disc.resolution_notes = res_in.resolution_notes

    # Update parcel
    if disc.parcel:
        disc.parcel.boundary_status = BoundaryStatus.VERIFIED
        disc.parcel.discrepancy_status = "Resolved via Hearing"

    db.add(Notification(
        title="Discrepancy Resolved",
        message=f"Discrepancy on Gat {disc.parcel.gat_number} resolved by {current_user.full_name}: {res_in.resolution_notes}",
        notification_type="SUCCESS"
    ))

    db.add(AuditLog(
        user_id=current_user.id,
        action="RESOLVED_DISCREPANCY",
        entity_name="Discrepancy",
        entity_id=str(disc.id),
        old_value="Open",
        new_value=f"Resolved: {res_in.resolution_notes}"
    ))

    db.commit()
    db.refresh(disc)
    
    p = disc.parcel
    owner = p.owners[0].farmer.full_name if p and p.owners else "N/A"
    return {
        "id": disc.id,
        "parcel_id": disc.parcel_id,
        "survey_id": disc.survey_id,
        "discrepancy_type": disc.discrepancy_type,
        "severity": disc.severity,
        "status": disc.status,
        "old_geometry_geojson": disc.old_geometry_geojson,
        "new_geometry_geojson": disc.new_geometry_geojson,
        "difference_geometry_geojson": disc.difference_geometry_geojson,
        "old_area_ha": disc.old_area_ha,
        "new_area_ha": disc.new_area_ha,
        "diff_area_ha": disc.diff_area_ha,
        "diff_percent": disc.diff_percent,
        "assigned_officer": disc.assigned_officer,
        "detected_date": disc.detected_date,
        "resolved_date": disc.resolved_date,
        "resolution_notes": disc.resolution_notes,
        "survey_number": p.survey_number if p else "",
        "gat_number": p.gat_number if p else "",
        "owner_name": owner,
        "village_name": p.village.name if p and p.village else ""
    }
