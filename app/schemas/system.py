from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_name: str
    entity_id: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: str
    created_at: datetime

    class Config:
        from_attributes = True

class NaturalLanguageQueryRequest(BaseModel):
    query: str

class NaturalLanguageQueryResponse(BaseModel):
    interpreted_query: str
    filters_applied: Dict[str, Any]
    results_count: int
    results: List[Dict[str, Any]]
    explanation: str

class OCRValidationResponse(BaseModel):
    extracted_text: str
    parsed_fields: Dict[str, Any]
    confidence_score: float
    matched_parcel_id: Optional[int] = None
    is_valid_match: bool
    inconsistencies: List[str] = []
