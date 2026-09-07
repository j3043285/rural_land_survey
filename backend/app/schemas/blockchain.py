"""
Blockchain Verification Schemas
Pydantic models for blockchain verification request/response.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BlockchainVerifyResponse(BaseModel):
    """Response model for blockchain verification."""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Status message")
    parcel_id: int = Field(..., description="ID of the verified parcel")
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    block_number: int = Field(..., description="Block number in the chain")
    document_hash: str = Field(..., description="SHA-256 hash of the document")
    verified_at: datetime = Field(..., description="Timestamp of verification")
    qr_code_url: Optional[str] = Field(None, description="URL to QR code certificate")

    class Config:
        from_attributes = True


class BlockchainIntegrityCheck(BaseModel):
    """Response model for integrity check."""
    valid: bool = Field(..., description="Whether the record is valid")
    message: str = Field(..., description="Validation message")
    parcel_id: int = Field(..., description="ID of the parcel checked")
    block_number: Optional[int] = Field(None, description="Block number if valid")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash if valid")
    verified_at: Optional[datetime] = Field(None, description="Original verification time")

    class Config:
        from_attributes = True


class BlockchainVerificationList(BaseModel):
    """List response for blockchain verifications."""
    total: int
    skip: int
    limit: int
    verifications: list[dict]
