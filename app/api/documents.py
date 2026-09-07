import os
import shutil
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.documents import Document
from app.models.parcels import LandParcel
from app.schemas.documents import DocumentResponse
from app.schemas.system import OCRValidationResponse
from app.ai.ocr_parser import mock_extract_and_validate_document
from app.api.deps import get_current_user
from app.models.users import User

router = APIRouter(prefix="/documents", tags=["Document Management & OCR"])

@router.get("", response_model=List[DocumentResponse])
def get_documents(
    parcel_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Document)
    if parcel_id:
        q = q.filter(Document.parcel_id == parcel_id)
    if document_type:
        q = q.filter(Document.document_type == document_type)
    return q.order_by(Document.created_at.desc()).all()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form("7/12 Extract"),
    parcel_id: Optional[int] = Form(None),
    survey_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    timestamp_prefix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{timestamp_prefix}_{file.filename.replace(' ', '_')}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    file_bytes = await file.read()
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
        
    file_size_kb = len(file_bytes) // 1024

    # Run OCR analysis simulation on text/content
    ocr_text = f"Form VII-XII Land Record Maharashtra: Parcel ID {parcel_id}, File {file.filename}, Uploaded by {current_user.full_name}."
    ocr_result = mock_extract_and_validate_document(ocr_text, file.filename, db)

    doc = Document(
        title=title,
        document_type=document_type,
        file_path=f"uploads/{safe_filename}",
        file_name=file.filename,
        file_size_kb=file_size_kb,
        mime_type=file.content_type or "application/octet-stream",
        parcel_id=parcel_id,
        survey_id=survey_id,
        uploaded_by=current_user.full_name,
        is_verified=ocr_result["is_valid_match"],
        ocr_extracted_text=ocr_result["extracted_text"],
        ocr_parsed_data=json.dumps(ocr_result["parsed_fields"])
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/ocr-validate", response_model=OCRValidationResponse)
def validate_document_ocr(
    content_text: str = Form(...),
    document_name: str = Form("7-12-Scanned.pdf"),
    db: Session = Depends(get_db)
):
    result = mock_extract_and_validate_document(content_text, document_name, db)
    return result
