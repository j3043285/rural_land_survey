"""
Blockchain Verification Models
Stores cryptographic hashes of land records for immutability.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class BlockchainVerification(Base):
    __tablename__ = "blockchain_verifications"

    id = Column(Integer, primary_key=True)
    parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False, index=True)
    
    # Cryptographic Hashes
    document_hash = Column(String(64), nullable=False)  # SHA-256 of the JSON record
    transaction_hash = Column(String(128), unique=True)  # Simulated Blockchain Tx ID
    previous_hash = Column(String(128))  # Link to previous state for chain integrity
    
    # Metadata
    block_number = Column(Integer, nullable=False)
    verified_by = Column(String(100), default="system_auto")
    verified_at = Column(DateTime, default=datetime.utcnow)
    
    # Certificate Info
    qr_code_path = Column(String(255))  # Path to generated QR certificate
    is_valid = Column(Boolean, default=True)

    # Relationships
    parcel = relationship("LandParcel", back_populates="blockchain_records")

    def __repr__(self):
        return f"<BlockchainVerification(parcel_id={self.parcel_id}, tx_hash={self.transaction_hash[:10]}...)"
