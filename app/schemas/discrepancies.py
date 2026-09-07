from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.discrepancies import DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus

class DiscrepancyResponse(BaseModel):
    id: int
    parcel_id: int
    survey_id: Optional[int] = None
    discrepancy_type: DiscrepancyType
    severity: DiscrepancySeverity
    status: DiscrepancyStatus
    old_geometry_geojson: Optional[str] = None
    new_geometry_geojson: Optional[str] = None
    difference_geometry_geojson: Optional[str] = None
    old_area_ha: float
    new_area_ha: float
    diff_area_ha: float
    diff_percent: float
    assigned_officer: str
    detected_date: datetime
    resolved_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    # Enriched fields
    survey_number: Optional[str] = None
    gat_number: Optional[str] = None
    owner_name: Optional[str] = None
    village_name: Optional[str] = None

    class Config:
        from_attributes = True

class DiscrepancyResolveRequest(BaseModel):
    status: DiscrepancyStatus = DiscrepancyStatus.RESOLVED
    resolution_notes: str
