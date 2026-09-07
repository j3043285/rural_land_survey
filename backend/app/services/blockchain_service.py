"""
Blockchain Verification Service
Generates SHA-256 hashes, simulates blockchain transactions, and creates QR certificates.
"""
import hashlib
import json
import uuid
import os
import qrcode
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.blockchain_verification import BlockchainVerification
from app.models.parcels import LandParcel


class BlockchainService:
    """
    Service to handle blockchain-like verification of land records.
    Since we cannot connect to a real public blockchain in a hackathon demo,
    we simulate the behavior using cryptographic hashing and a local ledger.
    """

    def __init__(self, db: Session):
        self.db = db
        self.current_block_height = self._get_latest_block_number()

    def _get_latest_block_number(self) -> int:
        """Get the current height of our simulated blockchain."""
        last_record = self.db.query(BlockchainVerification).order_by(
            BlockchainVerification.block_number.desc()
        ).first()
        return last_record.block_number if last_record else 0

    def generate_document_hash(self, parcel_data: Dict[str, Any]) -> str:
        """
        Generate a SHA-256 hash of the parcel data.
        Ensures consistent hashing by sorting keys.
        """
        # Remove non-deterministic fields (like updated_at) before hashing
        clean_data = {k: v for k, v in parcel_data.items() 
                      if k not in ['updated_at', 'last_verified']}
        
        data_str = json.dumps(clean_data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def create_transaction_hash(self, document_hash: str, previous_hash: str) -> str:
        """
        Simulate a blockchain transaction hash.
        Combines document hash, previous block hash, and timestamp.
        """
        timestamp = datetime.utcnow().isoformat()
        nonce = str(uuid.uuid4())
        
        raw_input = f"{document_hash}{previous_hash}{timestamp}{nonce}"
        return hashlib.sha256(raw_input.encode('utf-8')).hexdigest()

    def verify_parcel(self, parcel_id: int, verified_by: str = "system") -> BlockchainVerification:
        """
        Create a blockchain verification record for a land parcel.
        Returns the verification object containing the 'transaction' details.
        """
        parcel = self.db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
        if not parcel:
            raise ValueError(f"Parcel with ID {parcel_id} not found")

        # Prepare parcel data for hashing
        parcel_data = {
            "id": parcel.id,
            "survey_number": parcel.survey_number,
            "gat_number": parcel.gat_number,
            "area": parcel.area,
            "owner_name": parcel.owner_name,
            "village_id": parcel.village_id,
            "boundary_geojson": parcel.boundary_geojson
        }

        # Generate Hashes
        document_hash = self.generate_document_hash(parcel_data)
        
        # Get previous block hash for chain integrity
        last_block = self.db.query(BlockchainVerification).order_by(
            BlockchainVerification.block_number.desc()
        ).first()
        previous_hash = last_block.transaction_hash if last_block else "0" * 64

        # Create new block
        self.current_block_height += 1
        transaction_hash = self.create_transaction_hash(document_hash, previous_hash)

        # Save to DB
        verification = BlockchainVerification(
            parcel_id=parcel_id,
            document_hash=document_hash,
            transaction_hash=transaction_hash,
            previous_hash=previous_hash,
            block_number=self.current_block_height,
            verified_by=verified_by,
            verified_at=datetime.utcnow(),
            is_valid=True
        )

        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)

        # Generate QR Code
        qr_path = self.generate_qr_certificate(verification)
        verification.qr_code_path = qr_path
        self.db.commit()

        return verification

    def generate_qr_certificate(self, verification: BlockchainVerification) -> str:
        """
        Generate a QR code containing verification details.
        Saves the image to the static directory and returns the path.
        """
        # Data to encode in QR
        qr_data = {
            "tx_hash": verification.transaction_hash,
            "block": verification.block_number,
            "parcel_id": verification.parcel_id,
            "verified_at": verification.verified_at.isoformat(),
            "valid": verification.is_valid
        }
        
        qr_json = json.dumps(qr_data)
        
        # Ensure directory exists
        qr_dir = "backend/app/static/certificates"
        os.makedirs(qr_dir, exist_ok=True)
        
        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"cert_{verification.transaction_hash[:12]}.png"
        filepath = os.path.join(qr_dir, filename)
        
        img.save(filepath)
        
        # Return relative path for frontend access
        return f"/static/certificates/{filename}"

    def verify_integrity(self, parcel_id: int) -> Dict[str, Any]:
        """
        Verify if a parcel's current data matches its blockchain record.
        Returns validation status and details.
        """
        parcel = self.db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
        if not parcel:
            return {"valid": False, "error": "Parcel not found"}

        # Get latest verification for this parcel
        verification = self.db.query(BlockchainVerification).filter(
            BlockchainVerification.parcel_id == parcel_id
        ).order_by(BlockchainVerification.verified_at.desc()).first()

        if not verification:
            return {"valid": False, "error": "No blockchain record found"}

        # Recalculate hash from current data
        parcel_data = {
            "id": parcel.id,
            "survey_number": parcel.survey_number,
            "gat_number": parcel.gat_number,
            "area": parcel.area,
            "owner_name": parcel.owner_name,
            "village_id": parcel.village_id,
            "boundary_geojson": parcel.boundary_geojson
        }
        
        current_hash = self.generate_document_hash(parcel_data)

        if current_hash == verification.document_hash:
            return {
                "valid": True,
                "message": "Record integrity verified on blockchain",
                "block_number": verification.block_number,
                "tx_hash": verification.transaction_hash,
                "verified_at": verification.verified_at
            }
        else:
            return {
                "valid": False,
                "message": "WARNING: Record has been modified since blockchain verification!",
                "expected_hash": verification.document_hash,
                "current_hash": current_hash
            }
