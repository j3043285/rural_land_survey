from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.grievances import GrievanceStatus, GrievanceType


class GrievanceCreate(BaseModel):
    parcel_id: Optional[int] = None
    farmer_name: str = Field(min_length=2, max_length=150)
    farmer_phone: str = Field(min_length=7, max_length=30)
    preferred_language: str = Field(default="Marathi", max_length=20)
    grievance_type: GrievanceType = GrievanceType.OTHER
    description: str = Field(min_length=10, max_length=5000)


class GrievanceUpdate(BaseModel):
    status: GrievanceStatus
    assigned_officer: Optional[str] = None
    resolution_notes: Optional[str] = None


class GrievanceResponse(BaseModel):
    id: int
    ticket_number: str
    parcel_id: Optional[int] = None
    farmer_name: str
    farmer_phone: str
    preferred_language: str
    grievance_type: GrievanceType
    description: str
    status: GrievanceStatus
    assigned_officer: Optional[str] = None
    resolution_notes: Optional[str] = None
    due_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True