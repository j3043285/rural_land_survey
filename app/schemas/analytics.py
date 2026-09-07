from pydantic import BaseModel
from typing import List, Optional

class KpiStats(BaseModel):
    total_parcels: int
    surveyed_count: int
    surveyed_pct: float
    verified_count: int
    verified_pct: float
    discrepancy_count: int
    discrepancy_pct: float
    total_area_surveyed_ha: float
    area_surveyed_pct: float

class LandTypeDistributionItem(BaseModel):
    name: str
    percentage: float
    color: str
    area_ha: float

class AreaByTalukaItem(BaseModel):
    taluka: str
    area_ha: float

class RecentSurveyItem(BaseModel):
    id: int
    date: str
    survey_no: str
    area_ha: float
    status: str

class DashboardStatsResponse(BaseModel):
    kpis: KpiStats
    land_types: List[LandTypeDistributionItem]
    area_by_taluka: List[AreaByTalukaItem]
    recent_surveys: List[RecentSurveyItem]
