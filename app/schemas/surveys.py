from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.surveys import SurveyStatus

class SurveyPointBase(BaseModel):
    point_order: int
    latitude: float
    longitude: float
    elevation: Optional[float] = 0.0
    accuracy: Optional[float] = 0.5
    point_type: Optional[str] = "Boundary Corner"
    remarks: Optional[str] = None

class SurveyPointCreate(SurveyPointBase):
    pass

class SurveyPointResponse(SurveyPointBase):
    id: int
    survey_id: int
    captured_at: datetime

    class Config:
        from_attributes = True

class SurveyCreate(BaseModel):
    parcel_id: int
    survey_number: Optional[str] = None
    old_area_hectares: float
    new_area_hectares: float
    surveyor_remarks: Optional[str] = None
    gps_accuracy_meters: Optional[float] = 0.5
    points: Optional[List[SurveyPointCreate]] = []

class SurveyUpdate(BaseModel):
    new_area_hectares: Optional[float] = None
    surveyor_remarks: Optional[str] = None
    gps_accuracy_meters: Optional[float] = None
    points: Optional[List[SurveyPointCreate]] = None

class SurveyActionRequest(BaseModel):
    remarks: Optional[str] = None

class SurveyResponse(BaseModel):
    id: int
    survey_number: str
    parcel_id: int
    surveyor_id: int
    verified_by_id: Optional[int] = None
    status: SurveyStatus
    survey_date: datetime
    submission_date: Optional[datetime] = None
    verification_date: Optional[datetime] = None
    old_area_hectares: float
    new_area_hectares: float
    area_diff_hectares: float
    area_diff_percent: float
    gps_accuracy_meters: float
    surveyor_remarks: Optional[str] = None
    verification_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    points: List[SurveyPointResponse] = []

    class Config:
        from_attributes = True

class BoundaryComparisonResult(BaseModel):
    parcel_id: int
    survey_number: str
    old_area_ha: float
    new_area_ha: float
    diff_area_ha: float
    diff_percent: float
    exceeds_threshold: bool
    status: str
    discrepancy_type: Optional[str] = None
    severity: Optional[str] = None
    old_geojson: str
    new_geojson: str
    difference_geojson: Optional[str] = None
    recommendations: List[str] = []
