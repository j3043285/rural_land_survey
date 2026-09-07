"""
Dispute Prediction Schemas
Pydantic models for ML-based dispute prediction.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DisputePredictionRequest(BaseModel):
    """Request model for dispute prediction (optional, can use path params)."""
    parcel_id: Optional[int] = None
    include_factors: bool = True


class ContributingFactor(BaseModel):
    """Individual factor contributing to prediction."""
    factor: str = Field(..., description="Name of the feature")
    importance: float = Field(..., description="Feature importance score")
    value: float = Field(..., description="Actual value for this parcel")


class DisputePredictionResponse(BaseModel):
    """Response model for single parcel dispute prediction."""
    parcel_id: int = Field(..., description="ID of the parcel")
    survey_number: str = Field(..., description="Survey number")
    gat_number: str = Field(..., description="GAT number")
    
    dispute_probability: float = Field(..., description="Probability of dispute (0-1)")
    predicted_dispute: bool = Field(..., description="Binary prediction")
    risk_level: str = Field(..., description="Risk category: Low/Medium/High")
    risk_score: float = Field(..., description="Risk score (0-100)")
    
    contributing_factors: Optional[List[ContributingFactor]] = Field(
        None, description="Top factors contributing to prediction"
    )
    recommendation: str = Field(..., description="Actionable recommendation")

    class Config:
        from_attributes = True


class ParcelRiskSummary(BaseModel):
    """Simplified risk summary for bulk predictions."""
    parcel_id: int
    survey_number: str
    gat_number: str
    risk_level: str
    risk_score: float
    dispute_probability: float


class BulkDisputePredictionResponse(BaseModel):
    """Response model for bulk dispute prediction."""
    total_parcels: int = Field(..., description="Total parcels analyzed")
    high_risk_count: int = Field(..., description="Number of high-risk parcels")
    medium_risk_count: int = Field(..., description="Number of medium-risk parcels")
    low_risk_count: int = Field(..., description="Number of low-risk parcels")
    average_risk_score: float = Field(..., description="Average risk score across all parcels")
    predictions: List[ParcelRiskSummary] = Field(..., description="List of predictions")

    class Config:
        from_attributes = True


class RiskFactorInfo(BaseModel):
    """Information about a risk factor."""
    name: str
    description: str
    impact: str  # Low/Medium/High/Very High


class ModelInfo(BaseModel):
    """Information about the ML model."""
    algorithm: str
    training_data: str
    accuracy: str
    features_used: int


class RiskFactorsResponse(BaseModel):
    """Response for risk factors explanation endpoint."""
    factors: List[RiskFactorInfo]
    model_info: ModelInfo
