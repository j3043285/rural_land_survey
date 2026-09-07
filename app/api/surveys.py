from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
from app.core.database import get_db
from app.models.surveys import SurveyRecord, SurveyPoint, SurveyStatus
from app.models.parcels import LandParcel, BoundaryStatus
from app.models.users import User, UserRole
from app.models.system import AuditLog, Notification
from app.schemas.surveys import SurveyCreate, SurveyUpdate, SurveyResponse, SurveyActionRequest
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/surveys", tags=["Survey Workflow"])

@router.get("", response_model=List[SurveyResponse])
def get_surveys(
    parcel_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(SurveyRecord)
    if parcel_id:
        q = q.filter(SurveyRecord.parcel_id == parcel_id)
    if status:
        q = q.filter(SurveyRecord.status == status)
    return q.order_by(SurveyRecord.survey_date.desc()).all()

@router.post("", response_model=SurveyResponse)
def create_survey(
    survey_in: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parcel = db.query(LandParcel).filter(LandParcel.id == survey_in.parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
        
    diff_ha = round(survey_in.new_area_hectares - survey_in.old_area_hectares, 2)
    diff_pct = round(abs(diff_ha) / survey_in.old_area_hectares * 100.0, 1) if survey_in.old_area_hectares > 0 else 0.0

    surv_num = survey_in.survey_number or f"SURV-2025-{parcel.gat_number.replace('/', '-')}"

    survey = SurveyRecord(
        survey_number=surv_num,
        parcel_id=parcel.id,
        surveyor_id=current_user.id,
        status=SurveyStatus.IN_PROGRESS,
        survey_date=datetime.utcnow(),
        old_area_hectares=survey_in.old_area_hectares,
        new_area_hectares=survey_in.new_area_hectares,
        area_diff_hectares=diff_ha,
        area_diff_percent=diff_pct,
        gps_accuracy_meters=survey_in.gps_accuracy_meters or 0.5,
        surveyor_remarks=survey_in.surveyor_remarks
    )
    db.add(survey)
    db.flush()

    if survey_in.points:
        for p in survey_in.points:
            pt = SurveyPoint(
                survey_id=survey.id,
                point_order=p.point_order,
                latitude=p.latitude,
                longitude=p.longitude,
                elevation=p.elevation or 0.0,
                accuracy=p.accuracy or 0.5,
                point_type=p.point_type or "Boundary Corner",
                remarks=p.remarks
            )
            db.add(pt)

    # Update parcel status to In Progress
    parcel.boundary_status = BoundaryStatus.IN_PROGRESS
    parcel.last_survey_date = datetime.utcnow()

    db.add(AuditLog(
        user_id=current_user.id,
        action="CREATED_FIELD_SURVEY",
        entity_name="SurveyRecord",
        entity_id=surv_num,
        old_value="None",
        new_value=f"New Area: {survey_in.new_area_hectares} ha"
    ))

    db.commit()
    db.refresh(survey)
    return survey

@router.post("/{id}/submit", response_model=SurveyResponse)
def submit_survey(
    id: int, 
    action: SurveyActionRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    survey = db.query(SurveyRecord).filter(SurveyRecord.id == id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey record not found")
        
    survey.status = SurveyStatus.SUBMITTED
    survey.submission_date = datetime.utcnow()
    if action.remarks:
        survey.surveyor_remarks = f"{survey.surveyor_remarks or ''} | Submit: {action.remarks}".strip(" |")

    db.add(Notification(
        title="Survey Submitted for Verification",
        message=f"Survey #{survey.survey_number} for Gat {survey.parcel.gat_number} submitted by {current_user.full_name}.",
        notification_type="INFO",
        link=f"/resurvey"
    ))

    db.add(AuditLog(
        user_id=current_user.id,
        action="SUBMITTED_SURVEY",
        entity_name="SurveyRecord",
        entity_id=survey.survey_number,
        old_value="In Progress",
        new_value="Submitted"
    ))

    db.commit()
    db.refresh(survey)
    return survey

@router.post("/{id}/verify", response_model=SurveyResponse)
def verify_survey(
    id: int, 
    action: SurveyActionRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    survey = db.query(SurveyRecord).filter(SurveyRecord.id == id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey record not found")
        
    survey.status = SurveyStatus.VERIFIED
    survey.verified_by_id = current_user.id
    survey.verification_date = datetime.utcnow()
    survey.verification_remarks = action.remarks or "Verified and confirmed by Circle Officer."

    # Update parcel
    if survey.parcel:
        survey.parcel.boundary_status = BoundaryStatus.VERIFIED
        survey.parcel.area_hectares = survey.new_area_hectares
        survey.parcel.area_acres = round(survey.new_area_hectares * 2.47105, 2)
        survey.parcel.discrepancy_status = "No Discrepancy"
        survey.parcel.remarks = "Boundary matched and verified with DGPS"

    db.add(Notification(
        title="Parcel Survey Verified",
        message=f"Survey #{survey.survey_number} for Gat {survey.parcel.gat_number} verified and certified.",
        notification_type="SUCCESS",
        link=f"/parcel-records"
    ))

    db.add(AuditLog(
        user_id=current_user.id,
        action="VERIFIED_SURVEY",
        entity_name="SurveyRecord",
        entity_id=survey.survey_number,
        old_value="Submitted",
        new_value="Verified"
    ))

    db.commit()
    db.refresh(survey)
    return survey

@router.post("/{id}/reject", response_model=SurveyResponse)
def reject_survey(
    id: int, 
    action: SurveyActionRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    survey = db.query(SurveyRecord).filter(SurveyRecord.id == id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey record not found")
        
    survey.status = SurveyStatus.REJECTED
    survey.verified_by_id = current_user.id
    survey.rejection_reason = action.remarks or "Discrepancy in coordinates. Resurvey requested."

    if survey.parcel:
        survey.parcel.boundary_status = BoundaryStatus.DISCREPANCY
        survey.parcel.discrepancy_status = "Discrepancy Found (Rejected in Verification)"

    db.add(Notification(
        title="Survey Rejected",
        message=f"Survey #{survey.survey_number} for Gat {survey.parcel.gat_number} was rejected: {survey.rejection_reason}",
        notification_type="ERROR",
        link=f"/resurvey"
    ))

    db.add(AuditLog(
        user_id=current_user.id,
        action="REJECTED_SURVEY",
        entity_name="SurveyRecord",
        entity_id=survey.survey_number,
        old_value="Submitted",
        new_value="Rejected"
    ))

    db.commit()
    db.refresh(survey)
    return survey
