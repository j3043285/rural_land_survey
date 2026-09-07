"""
Dispute Prediction ML Model
Predicts likelihood of land disputes based on historical patterns and parcel features.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class DisputePredictor:
    """
    Machine Learning model to predict land dispute probability.
    
    Features used:
    - Parcel area
    - Number of owners
    - Ownership share distribution
    - Land type
    - Previous discrepancy history
    - Mutation count (transfers)
    - Time since last survey
    - Boundary status
    - Village-level dispute rate (historical)
    """
    
    def __init__(self, model_path: str = "backend/app/models/ml_models/dispute_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = [
            'area_hectares',
            'num_owners',
            'ownership_concentration',  # HHI index of ownership shares
            'land_type_encoded',
            'has_previous_discrepancy',
            'mutation_count',
            'days_since_last_survey',
            'boundary_status_encoded',
            'village_dispute_rate'
        ]
        
    def prepare_features(self, parcel_data: Dict[str, Any], context: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare feature vector from parcel data and context.
        
        Args:
            parcel_data: Dictionary containing parcel information
            context: Additional context (village stats, historical data)
        
        Returns:
            DataFrame with prepared features
        """
        features = {}
        
        # Area
        features['area_hectares'] = parcel_data.get('area_hectares', 0)
        
        # Ownership features
        owners = parcel_data.get('owners', [])
        num_owners = len(owners)
        features['num_owners'] = num_owners
        
        # Ownership concentration (Herfindahl-Hirschman Index)
        if num_owners > 0:
            shares = [o.get('ownership_share', 1.0) for o in owners]
            hhi = sum(s**2 for s in shares)
            features['ownership_concentration'] = hhi
        else:
            features['ownership_concentration'] = 1.0
        
        # Land type encoding
        land_type = parcel_data.get('land_type', 'Agricultural (Kharif)')
        if 'land_type_encoded' not in self.label_encoders:
            self.label_encoders['land_type'] = LabelEncoder()
            # Fit on common land types
            common_types = [
                'Agricultural (Kharif)', 'Agricultural (Rabi)', 'Horticulture',
                'Forest', 'Barren', 'Others'
            ]
            self.label_encoders['land_type'].fit(common_types)
        
        try:
            features['land_type_encoded'] = self.label_encoders['land_type'].transform([land_type])[0]
        except ValueError:
            features['land_type_encoded'] = 5  # Default to 'Others'
        
        # Discrepancy history
        has_discrepancy = 1 if parcel_data.get('discrepancy_status') == 'Discrepancy Found' else 0
        features['has_previous_discrepancy'] = has_discrepancy
        
        # Mutation count (number of transfers)
        mutations = parcel_data.get('mutations', [])
        features['mutation_count'] = len(mutations)
        
        # Days since last survey
        last_survey = parcel_data.get('last_survey_date')
        if last_survey:
            if isinstance(last_survey, str):
                last_survey = datetime.fromisoformat(last_survey.replace('Z', '+00:00'))
            days_since = (datetime.utcnow() - last_survey).days
            features['days_since_last_survey'] = max(0, days_since)
        else:
            features['days_since_last_survey'] = 365 * 10  # Default to 10 years
        
        # Boundary status encoding
        boundary_status = parcel_data.get('boundary_status', 'Pending')
        if 'boundary_status' not in self.label_encoders:
            self.label_encoders['boundary_status'] = LabelEncoder()
            statuses = ['Pending', 'In Progress', 'Verified', 'Discrepancy']
            self.label_encoders['boundary_status'].fit(statuses)
        
        try:
            features['boundary_status_encoded'] = self.label_encoders['boundary_status'].transform([boundary_status])[0]
        except ValueError:
            features['boundary_status_encoded'] = 0
        
        # Village-level dispute rate (from context)
        features['village_dispute_rate'] = context.get('village_dispute_rate', 0.1)
        
        return pd.DataFrame([features])
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'has_dispute'):
        """
        Train the dispute prediction model.
        
        Args:
            training_data: DataFrame with features and target column
            target_column: Name of the target column (binary: 0=no dispute, 1=dispute)
        """
        # Separate features and target
        X = training_data[self.feature_columns]
        y = training_data[target_column]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        print("Model Training Complete")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nFeature Importance:")
        print(feature_importance)
        
        return self
    
    def predict(self, parcel_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predict dispute probability for a parcel.
        
        Args:
            parcel_data: Dictionary with parcel information
            context: Optional context dictionary
        
        Returns:
            Dictionary with prediction results
        """
        if self.model is None:
            self.load_model()
        
        if context is None:
            context = {}
        
        # Prepare features
        X = self.prepare_features(parcel_data, context)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        probability = self.model.predict_proba(X_scaled)[0][1]  # Probability of dispute
        prediction = self.model.predict(X_scaled)[0]
        
        # Risk categorization
        if probability < 0.3:
            risk_level = "Low"
        elif probability < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Get top contributing factors
        feature_importance = self._get_feature_contributions(X_scaled)
        
        return {
            'dispute_probability': float(probability),
            'predicted_dispute': bool(prediction),
            'risk_level': risk_level,
            'risk_score': round(probability * 100, 2),
            'contributing_factors': feature_importance,
            'recommendation': self._generate_recommendation(probability, feature_importance)
        }
    
    def _get_feature_contributions(self, X_scaled: np.ndarray) -> List[Dict[str, Any]]:
        """Get top features contributing to the prediction."""
        if self.model is None:
            return []
        
        importances = self.model.feature_importances_
        feature_names = self.feature_columns
        
        # Sort by importance
        sorted_idx = np.argsort(importances)[::-1]
        
        contributions = []
        for idx in sorted_idx[:5]:  # Top 5 factors
            contributions.append({
                'factor': feature_names[idx],
                'importance': float(importances[idx]),
                'value': float(X_scaled[0][idx])
            })
        
        return contributions
    
    def _generate_recommendation(self, probability: float, factors: List[Dict]) -> str:
        """Generate actionable recommendation based on prediction."""
        if probability < 0.3:
            return "Low risk parcel. Continue regular monitoring schedule."
        elif probability < 0.6:
            return "Medium risk parcel. Consider proactive verification and owner communication."
        else:
            # Check top factors
            top_factor = factors[0]['factor'] if factors else ''
            
            if 'ownership' in top_factor.lower():
                return "High risk due to ownership complexity. Recommend immediate succession planning assistance."
            elif 'mutation' in top_factor.lower():
                return "High risk due to frequent transfers. Verify recent transactions and notify stakeholders."
            elif 'survey' in top_factor.lower():
                return "High risk due to outdated survey. Schedule immediate field verification."
            elif 'discrepancy' in top_factor.lower():
                return "High risk due to previous discrepancies. Initiate dispute resolution process."
            else:
                return "High risk parcel. Prioritize for detailed investigation and stakeholder consultation."
    
    def save_model(self):
        """Save the trained model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self, model_path: Optional[str] = None):
        """Load a trained model from disk."""
        path = model_path or self.model_path
        
        if not os.path.exists(path):
            print(f"No pre-trained model found at {path}. Training default model...")
            self._train_default_model()
            return
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        print(f"Model loaded from {path}")
    
    def _train_default_model(self):
        """Train a default model with synthetic data for demonstration."""
        print("Generating synthetic training data...")
        
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic data
        data = {
            'area_hectares': np.random.exponential(2, n_samples),
            'num_owners': np.random.poisson(2, n_samples) + 1,
            'ownership_concentration': np.random.beta(2, 5, n_samples) * 0.5 + 0.5,
            'land_type_encoded': np.random.randint(0, 6, n_samples),
            'has_previous_discrepancy': np.random.binomial(1, 0.2, n_samples),
            'mutation_count': np.random.poisson(1, n_samples),
            'days_since_last_survey': np.random.exponential(500, n_samples),
            'boundary_status_encoded': np.random.randint(0, 4, n_samples),
            'village_dispute_rate': np.random.beta(2, 10, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create synthetic target (dispute occurrence)
        # Higher probability if: many owners, high mutation count, previous discrepancy, old survey
        dispute_prob = (
            0.1 +
            0.15 * (df['num_owners'] > 3) +
            0.2 * (df['mutation_count'] > 2) +
            0.25 * df['has_previous_discrepancy'] +
            0.15 * (df['days_since_last_survey'] > 1000) +
            0.15 * (df['boundary_status_encoded'] == 3)  # Discrepancy status
        )
        
        df['has_dispute'] = np.random.binomial(1, dispute_prob.clip(0, 1))
        
        # Train on synthetic data
        self.train(df, target_column='has_dispute')
        
        # Save the model
        self.save_model()


# Singleton instance
_predictor_instance = None


def get_dispute_predictor() -> DisputePredictor:
    """Get or create the dispute predictor singleton."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DisputePredictor()
        _predictor_instance.load_model()
    return _predictor_instance


if __name__ == "__main__":
    # Example usage
    predictor = DisputePredictor()
    
    # Train with synthetic data (or load existing)
    predictor.load_model()
    
    # Test prediction
    test_parcel = {
        'area_hectares': 2.5,
        'owners': [
            {'ownership_share': 0.5},
            {'ownership_share': 0.3},
            {'ownership_share': 0.2}
        ],
        'land_type': 'Agricultural (Kharif)',
        'discrepancy_status': 'No Discrepancy',
        'mutations': [{'id': 1}, {'id': 2}],
        'last_survey_date': '2020-01-01',
        'boundary_status': 'Verified'
    }
    
    context = {
        'village_dispute_rate': 0.15
    }
    
    result = predictor.predict(test_parcel, context)
    print("\nPrediction Result:")
    print(result)
