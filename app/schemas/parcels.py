from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.parcels import BoundaryStatus

class FarmerResponse(BaseModel):
    id: int
    full_name: str
    aadhaar_masked: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

class ParcelOwnerResponse(BaseModel):
    id: int
    farmer: FarmerResponse
    ownership_share: float
    is_primary: int

    class Config:
        from_attributes = True

class CropRecordResponse(BaseModel):
    id: int
    season: str
    year: int
    crop_name: str
    area_covered: float
    irrigation_source: str

    class Config:
        from_attributes = True

class MutationRecordResponse(BaseModel):
    id: int
    ferfar_number: str
    mutation_date: datetime
    mutation_type: str
    details: str
    approved_by: str
    status: str

    class Config:
        from_attributes = True

class LandParcelBase(BaseModel):
    id: int
    survey_number: str
    gat_number: str
    khata_number: str
    village_id: int
    area_hectares: float
    area_acres: float
    land_type: str
    boundary_status: BoundaryStatus
    discrepancy_status: str
    center_lat: float
    center_lng: float
    remarks: Optional[str] = None
    last_survey_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class LandParcelResponse(LandParcelBase):
    plot_number: Optional[str] = None
    owner_name: Optional[str] = None
    village_name: Optional[str] = None
    taluka_name: Optional[str] = None
    district_name: Optional[str] = None

class LandParcelDetailResponse(LandParcelResponse):
    boundary_geojson: str
    old_boundary_geojson: Optional[str] = None
    owners: List[ParcelOwnerResponse] = []
    crops: List[CropRecordResponse] = []
    mutations: List[MutationRecordResponse] = []

class LandParcelUpdate(BaseModel):
    area_hectares: Optional[float] = None
    area_acres: Optional[float] = None
    land_type: Optional[str] = None
    boundary_status: Optional[BoundaryStatus] = None
    discrepancy_status: Optional[str] = None
    remarks: Optional[str] = None
    boundary_geojson: Optional[str] = None
