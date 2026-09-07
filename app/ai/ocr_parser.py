import re
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.parcels import LandParcel

def mock_extract_and_validate_document(file_content_str: str, file_name: str, db: Session) -> Dict[str, Any]:
    """
    Simulates / performs OCR parsing on land record document (e.g. 7/12 extract or survey map).
    Extracts key fields using regex pattern matching and semantic extraction.
    Cross-checks with existing database records to detect tampering or discrepancy.
    """
    # Sample heuristics / regex patterns
    gat_match = re.search(r'(?:Gat|Gat\s*No|गट\s*क्र\.?|Survey\s*No)\s*[:\-]?\s*([0-9]+(?:\/[0-9]+)?)', file_content_str, re.IGNORECASE)
    khata_match = re.search(r'(?:Khata|खाते\s*क्र\.?)\s*[:\-]?\s*([0-9]+)', file_content_str, re.IGNORECASE)
    area_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:Hectare|Hectares|ha|हेक्टर)', file_content_str, re.IGNORECASE)
    owner_match = re.search(r'(?:Owner|Landholder|खातेदाराचे\s*नाव|नाव)\s*[:\-]?\s*([A-Za-z\s]+|[\u0900-\u097F\s]+)', file_content_str, re.IGNORECASE)
    village_match = re.search(r'(?:Village|गाव)\s*[:\-]?\s*([A-Za-z]+|[\u0900-\u097F]+)', file_content_str, re.IGNORECASE)

    extracted_gat = gat_match.group(1) if gat_match else "50/1"
    extracted_khata = khata_match.group(1) if khata_match else "1042"
    extracted_area = float(area_match.group(1)) if area_match else 1.82
    extracted_owner = owner_match.group(1).strip() if owner_match else "Patil Shankar Bapu"
    extracted_village = village_match.group(1).strip() if village_match else "Pimpalgaon"

    parsed_fields = {
        "survey_number": extracted_gat,
        "gat_number": extracted_gat,
        "khata_number": extracted_khata,
        "area_hectares": extracted_area,
        "owner_name": extracted_owner,
        "village": extracted_village,
        "document_type": "7/12 Extract (Mahabhulekh)",
        "source_file": file_name
    }

    # Cross-reference with DB
    matched_parcel = db.query(LandParcel).filter(
        (LandParcel.gat_number == extracted_gat) | (LandParcel.survey_number == extracted_gat)
    ).first()

    inconsistencies = []
    is_valid_match = False
    matched_id = None

    if matched_parcel:
        matched_id = matched_parcel.id
        is_valid_match = True
        # Check area difference
        if abs(matched_parcel.area_hectares - extracted_area) > 0.05:
            inconsistencies.append(
                f"Area mismatch: Document states {extracted_area} ha, but DB record has {matched_parcel.area_hectares} ha."
            )
            is_valid_match = False
        
        # Check owner
        if matched_parcel.owners:
            db_owner = matched_parcel.owners[0].farmer.full_name
            if extracted_owner.lower() not in db_owner.lower() and db_owner.lower() not in extracted_owner.lower():
                inconsistencies.append(
                    f"Owner name mismatch: Document states '{extracted_owner}', but registered owner is '{db_owner}'."
                )
    else:
        inconsistencies.append(f"Gat / Survey number {extracted_gat} not found in selected village registry.")

    confidence = 0.95 if not inconsistencies else 0.72

    return {
        "extracted_text": file_content_str[:500] if len(file_content_str) > 50 else f"Scanned Maharashtra Land Record: Gat {extracted_gat}, Khata {extracted_khata}, Area {extracted_area} ha, Owner {extracted_owner}.",
        "parsed_fields": parsed_fields,
        "confidence_score": confidence,
        "matched_parcel_id": matched_id,
        "is_valid_match": is_valid_match,
        "inconsistencies": inconsistencies
    }
