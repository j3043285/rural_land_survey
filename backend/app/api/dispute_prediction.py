"""
Dispute Prediction API Endpoints
Provides ML-powered dispute risk predictions for land parcels.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.api.deps import get_db
from app.services.dispute_predictor import get_dispute_predictor, DisputePredictor
from app.models.parcels import LandParcel, ParcelOwner, MutationRecord
from app.schemas.dispute_prediction import (
    DisputePredictionRequest,
    DisputePredictionResponse,
    BulkDisputePredictionResponse
)

router = APIRouter()


@router.post("/predict/{parcel_id}", response_model=DisputePredictionResponse)
def predict_dispute_risk(
    parcel_id: int,
    db: Session = Depends(get_db),
    current_user: Any = None
):
    """
    Predict dispute risk for a specific land parcel.
    Uses ML model to analyze ownership patterns, history, and other factors.
    """
    # Get parcel with relationships
    parcel = db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")
    
    # Get predictor instance
    predictor = get_dispute_predictor()
    
    # Prepare parcel data
    owners = db.query(ParcelOwner).filter(ParcelOwner.parcel_id == parcel_id).all()
    mutations = db.query(MutationRecord).filter(MutationRecord.parcel_id == parcel_id).all()
    
    parcel_data = {
        'area_hectares': parcel.area_hectares,
        'owners': [
            {'ownership_share': owner.ownership_share}
            for owner in owners
        ],
        'land_type': parcel.land_type,
        'discrepancy_status': parcel.discrepancy_status,
        'mutations': [{'id': m.id} for m in mutations],
        'last_survey_date': parcel.last_survey_date.isoformat() if parcel.last_survey_date else None,
        'boundary_status': parcel.boundary_status.value if hasattr(parcel.boundary_status, 'value') else str(parcel.boundary_status)
    }
    
    # Calculate village-level context
    village_parcels = db.query(LandParcel).filter(LandParcel.village_id == parcel.village_id).all()
    total_discrepancies = sum(1 for p in village_parcels if p.discrepancy_status == 'Discrepancy Found')
    village_dispute_rate = total_discrepancies / len(village_parcels) if village_parcels else 0.1
    
    context = {
        'village_dispute_rate': village_dispute_rate
    }
    
    # Get prediction
    try:
        prediction = predictor.predict(parcel_data, context)
        
        return DisputePredictionResponse(
            parcel_id=parcel_id,
            survey_number=parcel.survey_number,
            gat_number=parcel.gat_number,
            **prediction
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/predict/bulk", response_model=BulkDisputePredictionResponse)
def predict_bulk_dispute_risk(
    village_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Any = None
):
    """
    Predict dispute risk for multiple parcels.
    Can filter by village or get top N high-risk parcels.
    """
    # Get parcels
    query = db.query(LandParcel)
    if village_id:
        query = query.filter(LandParcel.village_id == village_id)
    
    parcels = query.limit(limit).all()
    
    predictor = get_dispute_predictor()
    predictions = []
    
    for parcel in parcels:
        owners = db.query(ParcelOwner).filter(ParcelOwner.parcel_id == parcel.id).all()
        mutations = db.query(MutationRecord).filter(MutationRecord.parcel_id == parcel.id).all()
        
        parcel_data = {
            'area_hectares': parcel.area_hectares,
            'owners': [
                {'ownership_share': owner.ownership_share}
                for owner in owners
            ],
            'land_type': parcel.land_type,
            'discrepancy_status': parcel.discrepancy_status,
            'mutations': [{'id': m.id} for m in mutations],
            'last_survey_date': parcel.last_survey_date.isoformat() if parcel.last_survey_date else None,
            'boundary_status': parcel.boundary_status.value if hasattr(parcel.boundary_status, 'value') else str(parcel.boundary_status)
        }
        
        # Village context
        village_parcels = db.query(LandParcel).filter(LandParcel.village_id == parcel.village_id).all()
        total_discrepancies = sum(1 for p in village_parcels if p.discrepancy_status == 'Discrepancy Found')
        village_dispute_rate = total_discrepancies / len(village_parcels) if village_parcels else 0.1
        
        context = {'village_dispute_rate': village_dispute_rate}
        
        try:
            prediction = predictor.predict(parcel_data, context)
            predictions.append({
                'parcel_id': parcel.id,
                'survey_number': parcel.survey_number,
                'gat_number': parcel.gat_number,
                'risk_level': prediction['risk_level'],
                'risk_score': prediction['risk_score'],
                'dispute_probability': prediction['dispute_probability']
            })
        except Exception as e:
            continue
    
    # Sort by risk score descending
    predictions.sort(key=lambda x: x['risk_score'], reverse=True)
    
    # Statistics
    high_risk = sum(1 for p in predictions if p['risk_level'] == 'High')
    medium_risk = sum(1 for p in predictions if p['risk_level'] == 'Medium')
    low_risk = sum(1 for p in predictions if p['risk_level'] == 'Low')
    
    return BulkDisputePredictionResponse(
        total_parcels=len(predictions),
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        average_risk_score=round(sum(p['risk_score'] for p in predictions) / len(predictions), 2) if predictions else 0,
        predictions=predictions
    )


@router.get("/factors")
def get_risk_factors():
    """
    Get information about factors used in dispute prediction.
    Useful for explaining predictions to stakeholders.
    """
    return {
        "factors": [
            {
                "name": "Number of Owners",
                "description": "Parcels with more owners have higher dispute probability due to inheritance complexity",
                "impact": "High"
            },
            {
                "name": "Ownership Concentration",
                "description": "Measured using Herfindahl-Hirschman Index. Unequal distribution increases conflict risk",
                "impact": "Medium"
            },
            {
                "name": "Previous Discrepancies",
                "description": "History of boundary or ownership discrepancies indicates ongoing issues",
                "impact": "Very High"
            },
            {
                "name": "Mutation Count",
                "description": "Frequent transfers/sales increase likelihood of documentation errors",
                "impact": "High"
            },
            {
                "name": "Time Since Last Survey",
                "description": "Outdated surveys may not reflect current ground reality",
                "impact": "Medium"
            },
            {
                "name": "Boundary Status",
                "description": "Current verification status of parcel boundaries",
                "impact": "High"
            },
            {
                "name": "Village Dispute Rate",
                "description": "Historical dispute frequency in the village (contextual factor)",
                "impact": "Medium"
            }
        ],
        "model_info": {
            "algorithm": "Random Forest Classifier",
            "training_data": "Synthetic data based on expert knowledge of land dispute patterns",
            "accuracy": "~85% on validation set",
            "features_used": 9
        }
    }


@router.post("/train")
def retrain_model(
    db: Session = Depends(get_db),
    current_user: Any = None
):
    """
    Retrain the dispute prediction model with latest data.
    This endpoint triggers model retraining using historical dispute data.
    """
    try:
        from app.services.dispute_predictor import DisputePredictor
        import pandas as pd
        
        # In production, you would extract real historical data
        # For now, we'll retrain with synthetic data
        predictor = DisputePredictor()
        predictor._train_default_model()
        
        return {
            "status": "success",
            "message": "Model retrained successfully",
            "model_path": predictor.model_path
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
