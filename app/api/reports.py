from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.parcels import LandParcel
from app.reports.pdf_generator import generate_parcel_survey_pdf
from app.api.parcels import enrich_parcel

router = APIRouter(prefix="/reports", tags=["Reports & Certificate Generation"])

@router.get("/parcel/{id}/pdf")
def get_parcel_pdf_report(id: int, db: Session = Depends(get_db)):
    parcel = db.query(LandParcel).filter(LandParcel.id == id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
        
    enriched = enrich_parcel(parcel)
    pdf_bytes = generate_parcel_survey_pdf(enriched)
    
    filename = f"LandSetu_Survey_Report_Gat_{parcel.gat_number.replace('/', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
