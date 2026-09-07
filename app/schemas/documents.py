from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    title: str
    document_type: str
    file_path: str
    file_name: str
    file_size_kb: int
    mime_type: str
    parcel_id: Optional[int] = None
    survey_id: Optional[int] = None
    farmer_id: Optional[int] = None
    uploaded_by: str
    is_verified: bool
    ocr_extracted_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
