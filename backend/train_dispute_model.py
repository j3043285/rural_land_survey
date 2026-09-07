"""
Dispute Prediction ML Model Training Script
Train and save the dispute prediction model for production use.
Run this script to generate a new model file before deployment.
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dispute_predictor import DisputePredictor


def generate_synthetic_training_data(n_samples=1000):
    """
    Generate synthetic training data for dispute prediction.
    In production, replace with real historical data from Maharashtra land records.
    """
    np.random.seed(42)
    
    # Features
    area_hectares = np.random.exponential(2.5, n_samples) + 0.5
    num_owners = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.5, 0.25, 0.15, 0.07, 0.03])
    
    # Ownership concentration (HHI index)
    ownership_concentration = []
    for n in num_owners:
        if n == 1:
            ownership_concentration.append(1.0)
        else:
            shares = np.random.dirichlet(np.ones(n))
            hhi = np.sum(shares ** 2)
            ownership_concentration.append(hhi)
    ownership_concentration = np.array(ownership_concentration)
    
    land_type_encoded = np.random.choice([0, 1, 2, 3, 4, 5], n_samples, p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
    has_previous_discrepancy = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    mutation_count = np.random.poisson(2, n_samples)
    days_since_last_survey = np.random.exponential(365, n_samples) + 30
    boundary_status_encoded = np.random.choice([0, 1, 2], n_samples, p=[0.8, 0.15, 0.05])
    village_dispute_rate = np.random.beta(2, 5, n_samples)
    
    # Create feature matrix
    X = np.column_stack([
        area_hectares,
        num_owners,
        ownership_concentration,
        land_type_encoded,
        has_previous_discrepancy,
        mutation_count,
        days_since_last_survey,
        boundary_status_encoded,
        village_dispute_rate
    ])
    
    # Generate target variable (dispute occurred or not)
    # Higher probability if: many owners, low concentration, previous discrepancy, high village rate
    dispute_probability = (
        0.1 * (num_owners > 2) +
        0.15 * (ownership_concentration < 0.5) +
        0.25 * has_previous_discrepancy +
        0.1 * (mutation_count > 3) +
        0.15 * (boundary_status_encoded == 2) +
        0.2 * (village_dispute_rate > 0.3) +
        np.random.normal(0, 0.1, n_samples)
    )
    dispute_probability = np.clip(dispute_probability, 0, 1)
    y = (dispute_probability > 0.4).astype(int)
    
    return X, y


def train_model(output_path="ml_models/dispute_predictor.pkl"):
    """
    Train the dispute prediction model and save it.
    """
    print("🔧 Starting model training...")
    print("=" * 60)
    
    # Generate training data
    print("\n📊 Generating synthetic training data...")
    X, y = generate_synthetic_training_data(n_samples=2000)
    
    print(f"   Total samples: {len(X)}")
    print(f"   Positive class (disputes): {sum(y)} ({100*sum(y)/len(y):.1f}%)")
    print(f"   Negative class (no disputes): {len(y) - sum(y)} ({100*(len(y)-sum(y))/len(y):.1f}%)")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # Train Random Forest model
    print("\n🤖 Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n📈 Evaluating model performance...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n   Accuracy: {accuracy:.4f} ({100*accuracy:.2f}%)")
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Dispute', 'Dispute']))
    
    print("\n   Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"   True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"   False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
    
    # Feature importance
    print("\n📊 Feature Importance:")
    feature_names = [
        'area_hectares',
        'num_owners',
        'ownership_concentration',
        'land_type_encoded',
        'has_previous_discrepancy',
        'mutation_count',
        'days_since_last_survey',
        'boundary_status_encoded',
        'village_dispute_rate'
    ]
    
    importances = model.feature_importances_
    for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
        print(f"   {name:30s}: {imp:.4f}")
    
    # Save model
    print(f"\n💾 Saving model to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(model, output_path)
    
    print("\n✅ Model training completed successfully!")
    print("=" * 60)
    
    return model, accuracy


if __name__ == "__main__":
    output_path = "ml_models/dispute_predictor.pkl"
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    model, accuracy = train_model(output_path)
    
    # Verify model can be loaded
    print("\n🔍 Verifying saved model...")
    loaded_model = joblib.load(output_path)
    test_sample = np.array([[2.5, 2, 0.6, 0, 1, 1, 400, 0, 0.2]])
    prediction = loaded_model.predict(test_sample)
    probability = loaded_model.predict_proba(test_sample)[0, 1]
    
    print(f"   Test prediction: {'DISPUTE' if prediction[0] == 1 else 'NO DISPUTE'}")
    print(f"   Probability: {probability:.4f}")
    print("   Model verification successful! ✅")
