from pydantic import BaseModel
from typing import Optional, List

class VillageBase(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    taluka_id: int
    center_lat: float
    center_lng: float
    boundary_geojson: Optional[str] = None

    class Config:
        from_attributes = True

class TalukaBase(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    district_id: int
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None

    class Config:
        from_attributes = True

class DistrictBase(BaseModel):
    id: int
    name: str
    state: str
    code: Optional[str] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None

    class Config:
        from_attributes = True

class LocationSyncResponse(BaseModel):
    provider: str
    districts: int
    talukas: int
    villages: int
