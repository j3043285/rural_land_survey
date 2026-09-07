"""
Blockchain Verification API Endpoints
Provides endpoints for verifying land parcels on blockchain and generating certificates.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api.deps import get_db
from app.services.blockchain_service import BlockchainService
from app.schemas.blockchain import BlockchainVerifyResponse, BlockchainIntegrityCheck

router = APIRouter()


@router.post("/verify/{parcel_id}", response_model=BlockchainVerifyResponse)
def verify_parcel_on_blockchain(
    parcel_id: int,
    db: Session = Depends(get_db),
    current_user: Any = None  # Add auth later if needed
):
    """
    Verify a land parcel on the blockchain.
    Generates a cryptographic hash, creates a transaction record,
    and generates a QR code certificate.
    """
    try:
        blockchain_service = BlockchainService(db)
        verification = blockchain_service.verify_parcel(parcel_id, verified_by="system")
        
        return BlockchainVerifyResponse(
            success=True,
            message="Parcel successfully verified on blockchain",
            parcel_id=verification.parcel_id,
            transaction_hash=verification.transaction_hash,
            block_number=verification.block_number,
            document_hash=verification.document_hash,
            verified_at=verification.verified_at,
            qr_code_url=verification.qr_code_path
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/verify/{parcel_id}/check", response_model=BlockchainIntegrityCheck)
def check_parcel_integrity(
    parcel_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if a parcel's current data matches its blockchain record.
    Returns validation status and details.
    """
    blockchain_service = BlockchainService(db)
    result = blockchain_service.verify_integrity(parcel_id)
    
    if not result.get("valid"):
        if result.get("error") == "Parcel not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        elif result.get("error") == "No blockchain record found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No blockchain record found. Please verify the parcel first."
            )
    
    return BlockchainIntegrityCheck(
        valid=result["valid"],
        message=result["message"],
        parcel_id=parcel_id,
        block_number=result.get("block_number"),
        transaction_hash=result.get("tx_hash"),
        verified_at=result.get("verified_at")
    )


@router.get("/list")
def list_blockchain_verifications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List recent blockchain verifications.
    """
    from app.models.blockchain_verification import BlockchainVerification
    
    verifications = db.query(BlockchainVerification).order_by(
        BlockchainVerification.verified_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(BlockchainVerification).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "verifications": [
            {
                "id": v.id,
                "parcel_id": v.parcel_id,
                "transaction_hash": v.transaction_hash,
                "block_number": v.block_number,
                "verified_at": v.verified_at,
                "qr_code_url": v.qr_code_path
            }
            for v in verifications
        ]
    }
