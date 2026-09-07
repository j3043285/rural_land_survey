import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.parcels import LandParcel, BoundaryStatus, Farmer, ParcelOwner
from app.models.locations import Village, Taluka, District

def process_natural_language_query(query: str, db: Session) -> Dict[str, Any]:
    """
    Parses natural language requests such as:
    - "Show all agricultural parcels above 2 hectares in Yeola"
    - "Find parcels with discrepancy in Pimpalgaon"
    - "Show verified parcels owned by Patil"
    Converts them into safe structured query filters and executes against DB.
    """
    query_lower = query.lower()
    filters_applied = {}
    explanation_parts = []
    
    q = db.query(LandParcel)
    
    # 1. Location extraction
    # Check for taluka or village mentions
    villages = db.query(Village).all()
    talukas = db.query(Taluka).all()
    
    matched_village = next((v for v in villages if v.name.lower() in query_lower), None)
    if matched_village:
        q = q.filter(LandParcel.village_id == matched_village.id)
        filters_applied["village"] = matched_village.name
        explanation_parts.append(f"Filtered to village: {matched_village.name}")
    else:
        matched_taluka = next((t for t in talukas if t.name.lower() in query_lower), None)
        if matched_taluka:
            village_ids = [v.id for v in matched_taluka.villages]
            q = q.filter(LandParcel.village_id.in_(village_ids))
            filters_applied["taluka"] = matched_taluka.name
            explanation_parts.append(f"Filtered to taluka: {matched_taluka.name}")

    # 2. Status check
    if "discrepancy" in query_lower:
        q = q.filter((LandParcel.boundary_status == BoundaryStatus.DISCREPANCY) | (LandParcel.discrepancy_status.like("%Discrepancy%")))
        filters_applied["status"] = "Discrepancy"
        explanation_parts.append("Filtered parcels with detected boundary/area discrepancy")
    elif "verified" in query_lower:
        q = q.filter(LandParcel.boundary_status == BoundaryStatus.VERIFIED)
        filters_applied["status"] = "Verified"
        explanation_parts.append("Filtered only verified parcels")
    elif "in progress" in query_lower:
        q = q.filter(LandParcel.boundary_status == BoundaryStatus.IN_PROGRESS)
        filters_applied["status"] = "In Progress"
        explanation_parts.append("Filtered in-progress surveys")

    # 3. Area threshold extraction (e.g. "above 2 hectares", "> 3 ha", "less than 1.5 ha")
    above_match = re.search(r'(?:above|greater than|more than|>|over)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:ha|hectare|hectares)?', query_lower)
    below_match = re.search(r'(?:below|less than|under|<)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:ha|hectare|hectares)?', query_lower)
    
    if above_match:
        min_area = float(above_match.group(1))
        q = q.filter(LandParcel.area_hectares >= min_area)
        filters_applied["min_area_ha"] = min_area
        explanation_parts.append(f"Area >= {min_area} ha")
    elif below_match:
        max_area = float(below_match.group(1))
        q = q.filter(LandParcel.area_hectares <= max_area)
        filters_applied["max_area_ha"] = max_area
        explanation_parts.append(f"Area <= {max_area} ha")

    # 4. Land type
    if "agricultural" in query_lower:
        q = q.filter(LandParcel.land_type.like("%Agricultural%"))
        filters_applied["land_type"] = "Agricultural"
        explanation_parts.append("Land type: Agricultural")
    elif "horticulture" in query_lower:
        q = q.filter(LandParcel.land_type.like("%Horticulture%"))
        filters_applied["land_type"] = "Horticulture"
        explanation_parts.append("Land type: Horticulture")
    elif "forest" in query_lower:
        q = q.filter(LandParcel.land_type.like("%Forest%"))
        filters_applied["land_type"] = "Forest"
        explanation_parts.append("Land type: Forest")

    # 5. Owner name search check
    owner_match = re.search(r'(?:owner|farmer|owned by|named)\s+([A-Za-z]+)', query_lower)
    if owner_match:
        name_term = owner_match.group(1)
        q = q.join(LandParcel.owners).join(ParcelOwner.farmer).filter(Farmer.full_name.ilike(f"%{name_term}%"))
        filters_applied["owner_keyword"] = name_term
        explanation_parts.append(f"Owner matching '{name_term}'")

    results = q.limit(20).all()

    formatted_results = []
    for p in results:
        primary_owner = p.owners[0].farmer.full_name if p.owners else "N/A"
        formatted_results.append({
            "id": p.id,
            "survey_number": p.survey_number,
            "gat_number": p.gat_number,
            "area_ha": p.area_hectares,
            "land_type": p.land_type,
            "boundary_status": p.boundary_status.value,
            "owner_name": primary_owner,
            "village": p.village.name if p.village else "Unknown",
            "center_lat": p.center_lat,
            "center_lng": p.center_lng
        })

    explanation = "; ".join(explanation_parts) if explanation_parts else "All matching land records retrieved."

    return {
        "interpreted_query": query,
        "filters_applied": filters_applied,
        "results_count": len(formatted_results),
        "results": formatted_results,
        "explanation": explanation
    }
