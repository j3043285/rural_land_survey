from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.integrations.factory import get_land_record_provider
from app.models.locations import District, Taluka, Village
from app.schemas.locations import DistrictBase, LocationSyncResponse, TalukaBase, VillageBase

router = APIRouter(tags=["Locations & Administrative Boundaries"])

@router.get("/districts", response_model=List[DistrictBase])
def get_districts(db: Session = Depends(get_db)):
    return db.query(District).all()

@router.get("/talukas", response_model=List[TalukaBase])
def get_talukas(district_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Taluka)
    if district_id is not None:
        q = q.filter(Taluka.district_id == district_id)
    return q.all()

@router.get("/villages", response_model=List[VillageBase])
def get_villages(taluka_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Village)
    if taluka_id is not None:
        q = q.filter(Village.taluka_id == taluka_id)
    return q.all()

def _items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("data", payload.get("items", []))
    return []

def _value(item, *keys, default=None):
    for key in keys:
        if item.get(key) is not None:
            return item[key]
    return default

@router.post("/locations/sync", response_model=LocationSyncResponse)
def sync_locations(db: Session = Depends(get_db)):
    provider = get_land_record_provider()
    if provider.__class__.__name__ != "MahabhulekhAdapter":
        raise HTTPException(status_code=400, detail="Set LAND_DATA_PROVIDER=official and configure the Mahabhumi API credentials first.")

    try:
        remote_districts = _items(provider.get_districts())
        district_count = taluka_count = village_count = 0

        for remote in remote_districts:
            remote_id = _value(remote, "id", "district_id", "code")
            name = _value(remote, "name", "district_name")
            if remote_id is None or not name:
                continue
            district = db.query(District).filter(District.name == name).first()
            if district is None:
                district = District(name=name, state="Maharashtra")
                db.add(district)
                db.flush()
            district.code = _value(remote, "code", "district_code", default=district.code)
            district_count += 1

            for remote_taluka in _items(provider.get_talukas(remote_id)):
                taluka_remote_id = _value(remote_taluka, "id", "taluka_id", "code")
                taluka_name = _value(remote_taluka, "name", "taluka_name")
                if taluka_remote_id is None or not taluka_name:
                    continue
                taluka = db.query(Taluka).filter(
                    Taluka.district_id == district.id, Taluka.name == taluka_name
                ).first()
                if taluka is None:
                    taluka = Taluka(name=taluka_name, district_id=district.id)
                    db.add(taluka)
                    db.flush()
                taluka.code = _value(remote_taluka, "code", "taluka_code", default=taluka.code)
                taluka_count += 1

                for remote_village in _items(provider.get_villages(taluka_remote_id)):
                    village_name = _value(remote_village, "name", "village_name")
                    if not village_name:
                        continue
                    village = db.query(Village).filter(
                        Village.taluka_id == taluka.id, Village.name == village_name
                    ).first()
                    if village is None:
                        village = Village(
                            name=village_name,
                            taluka_id=taluka.id,
                            center_lat=float(_value(remote_village, "center_lat", "latitude", default=0.0)),
                            center_lng=float(_value(remote_village, "center_lng", "longitude", default=0.0)),
                        )
                        db.add(village)
                    village.code = _value(remote_village, "code", "village_code", default=village.code)
                    village.boundary_geojson = _value(remote_village, "boundary_geojson", default=village.boundary_geojson)
                    village_count += 1

        db.commit()
        return LocationSyncResponse(provider="mahabhumi", districts=district_count, talukas=taluka_count, villages=village_count)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Mahabhumi location sync failed: {exc}") from exc
