import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.parcels import LandParcel, Farmer, ParcelOwner, BoundaryStatus
from app.models.locations import Village, Taluka, District
from app.models.surveys import SurveyRecord, SurveyStatus
from app.models.discrepancies import Discrepancy, DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus
from app.models.system import AuditLog
from app.schemas.parcels import LandParcelResponse, LandParcelDetailResponse, LandParcelUpdate
from app.schemas.surveys import BoundaryComparisonResult
from app.gis.geometry import compare_boundaries, calculate_polygon_area_ha
from app.api.deps import get_current_user
from app.models.users import User

router = APIRouter(prefix="/parcels", tags=["Land Parcels"])

def enrich_parcel(p: LandParcel) -> Dict[str, Any]:
    primary_owner = p.owners[0].farmer.full_name if p.owners else "N/A"
    return {
        "id": p.id,
        "survey_number": p.survey_number,
        "gat_number": p.gat_number,
        "plot_number": p.gat_number,
        "khata_number": p.khata_number,
        "village_id": p.village_id,
        "area_hectares": p.area_hectares,
        "area_acres": p.area_acres,
        "land_type": p.land_type,
        "boundary_status": p.boundary_status,
        "discrepancy_status": p.discrepancy_status,
        "center_lat": p.center_lat,
        "center_lng": p.center_lng,
        "remarks": p.remarks,
        "last_survey_date": p.last_survey_date,
        "owner_name": primary_owner,
        "village_name": p.village.name if p.village else "",
        "taluka_name": p.village.taluka.name if p.village and p.village.taluka else "",
        "district_name": p.village.taluka.district.name if p.village and p.village.taluka and p.village.taluka.district else "",
        "boundary_geojson": p.boundary_geojson,
        "old_boundary_geojson": p.old_boundary_geojson,
        "owners": p.owners,
        "crops": p.crops,
        "mutations": p.mutations
    }

@router.get("", response_model=List[LandParcelResponse])
def get_parcels(
    village_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    q = db.query(LandParcel)
    if village_id is not None:
        q = q.filter(LandParcel.village_id == village_id)
    if status is not None:
        q = q.filter(LandParcel.boundary_status == status)
    
    parcels = q.offset(skip).limit(limit).all()
    return [enrich_parcel(p) for p in parcels]

@router.get("/search", response_model=List[LandParcelResponse])
def search_parcels(
    q: str = Query(..., min_length=1, description="Search by survey number, plot/Gat number, Khata number, owner name, or village"),
    village_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    term = f"%{q.strip()}%"
    query = (
        db.query(LandParcel)
        .outerjoin(LandParcel.owners)
        .outerjoin(ParcelOwner.farmer)
        .outerjoin(LandParcel.village)
        .outerjoin(Village.taluka)
        .outerjoin(Taluka.district)
    )
    
    if village_id:
        query = query.filter(LandParcel.village_id == village_id)

    query = query.filter(
        or_(
            LandParcel.survey_number.ilike(term),
            LandParcel.gat_number.ilike(term),
            LandParcel.khata_number.ilike(term),
            Farmer.full_name.ilike(term),
            Village.name.ilike(term),
            Taluka.name.ilike(term),
            District.name.ilike(term)
        )
    ).distinct()

    results = query.limit(30).all()
    return [enrich_parcel(p) for p in results]

@router.get("/geojson/village/{village_id}")
def get_village_parcels_geojson(village_id: int, db: Session = Depends(get_db)):
    """
    Returns GeoJSON FeatureCollection of all parcels for the selected village.
    Used by Leaflet map to render cadastral plots with status-based colors.
    """
    parcels = db.query(LandParcel).filter(LandParcel.village_id == village_id).all()
    features = []
    
    for p in parcels:
        primary_owner = p.owners[0].farmer.full_name if p.owners else "Unknown"
        try:
            geom = json.loads(p.boundary_geojson)
        except Exception:
            geom = {
                "type": "Polygon",
                "coordinates": [[[p.center_lng - 0.001, p.center_lat - 0.001],
                                 [p.center_lng + 0.001, p.center_lat - 0.001],
                                 [p.center_lng + 0.001, p.center_lat + 0.001],
                                 [p.center_lng - 0.001, p.center_lat + 0.001],
                                 [p.center_lng - 0.001, p.center_lat - 0.001]]]
            }
            
        features.append({
            "type": "Feature",
            "id": p.id,
            "properties": {
                "id": p.id,
                "survey_number": p.survey_number,
                "gat_number": p.gat_number,
                "khata_number": p.khata_number,
                "owner_name": primary_owner,
                "area_hectares": p.area_hectares,
                "area_acres": p.area_acres,
                "land_type": p.land_type,
                "boundary_status": p.boundary_status.value,
                "discrepancy_status": p.discrepancy_status,
                "remarks": p.remarks,
                "center_lat": p.center_lat,
                "center_lng": p.center_lng
            },
            "geometry": geom
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/{id}", response_model=LandParcelDetailResponse)
def get_parcel_by_id(id: int, db: Session = Depends(get_db)):
    parcel = db.query(LandParcel).filter(LandParcel.id == id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
    return enrich_parcel(parcel)

@router.put("/{id}", response_model=LandParcelDetailResponse)
def update_parcel(
    id: int, 
    parcel_in: LandParcelUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parcel = db.query(LandParcel).filter(LandParcel.id == id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
        
    old_val_str = f"Area: {parcel.area_hectares} ha, Status: {parcel.boundary_status.value}"
    
    if parcel_in.area_hectares is not None:
        parcel.area_hectares = parcel_in.area_hectares
        parcel.area_acres = round(parcel_in.area_hectares * 2.47105, 2)
    if parcel_in.land_type is not None:
        parcel.land_type = parcel_in.land_type
    if parcel_in.boundary_status is not None:
        parcel.boundary_status = parcel_in.boundary_status
    if parcel_in.discrepancy_status is not None:
        parcel.discrepancy_status = parcel_in.discrepancy_status
    if parcel_in.remarks is not None:
        parcel.remarks = parcel_in.remarks
    if parcel_in.boundary_geojson is not None:
        parcel.boundary_geojson = parcel_in.boundary_geojson
        # Recalculate area
        ha, ac = calculate_polygon_area_ha(parcel_in.boundary_geojson)
        if ha > 0:
            parcel.area_hectares = ha
            parcel.area_acres = ac

    db.add(AuditLog(
        user_id=current_user.id,
        action="UPDATED_PARCEL_BOUNDARY",
        entity_name="LandParcel",
        entity_id=str(parcel.gat_number),
        old_value=old_val_str,
        new_value=f"Area: {parcel.area_hectares} ha, Status: {parcel.boundary_status.value}"
    ))

    db.commit()
    db.refresh(parcel)
    return enrich_parcel(parcel)

@router.post("/{id}/compare-boundary", response_model=BoundaryComparisonResult)
def compare_parcel_boundary(id: int, db: Session = Depends(get_db)):
    parcel = db.query(LandParcel).filter(LandParcel.id == id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
        
    old_geo = parcel.old_boundary_geojson or parcel.boundary_geojson
    new_geo = parcel.boundary_geojson

    result = compare_boundaries(old_geo, new_geo)
    
    return {
        "parcel_id": parcel.id,
        "survey_number": parcel.survey_number,
        "old_area_ha": result["old_area_ha"],
        "new_area_ha": result["new_area_ha"],
        "diff_area_ha": result["diff_area_ha"],
        "diff_percent": result["diff_percent"],
        "exceeds_threshold": result["exceeds_threshold"],
        "status": result["status"],
        "discrepancy_type": result["discrepancy_type"],
        "severity": result["severity"],
        "old_geojson": result["old_geojson"],
        "new_geojson": result["new_geojson"],
        "difference_geojson": result["difference_geojson"],
        "recommendations": result["recommendations"]
    }
