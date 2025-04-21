#!/usr/bin/env python
"""
Script to train the predictive models for SmartShelf
"""
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the predictor package
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    logger.info("Successfully imported scikit-learn")
except ImportError:
    logger.error("scikit-learn is not installed. Please install it with: pip install scikit-learn")
    sys.exit(1)

# Set USE_PREDICTOR to False to always use the fallback method
USE_PREDICTOR = False
logger.warning("Using fallback implementation for model training")

# Set up model output paths
MODELS_DIR = Path("/app/backend/app/models/trained")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RISK_MODEL_PATH = MODELS_DIR / "risk_model.joblib"
TIME_SERIES_MODELS_PATH = MODELS_DIR / "time_series_models.joblib"

logger.info(f"Models will be saved to: {MODELS_DIR}")
logger.info(f"Risk model path: {RISK_MODEL_PATH}")
logger.info(f"Time series models path: {TIME_SERIES_MODELS_PATH}")

def generate_sample_data(n_samples=1000):
    """Generate sample data for training models"""
    np.random.seed(42)
    data = {
        'vida_util_subsecao': np.random.randint(30, 180, n_samples),
        'unidades_vendidas_90dias': np.random.randint(0, 100, n_samples),
        'estoque_atual': np.random.randint(5, 50, n_samples),
        'secao': np.random.choice(['JARDIM', 'PINTURA', 'ELETRICA', 'HIDRAULICA'], n_samples),
        'cd_subsecao': np.random.randint(1, 10, n_samples),
        'cd_loja': np.random.choice(['LOJA_1', 'LOJA_2', 'LOJA_3', 'LOJA_4'], n_samples),
        'eh_sazonal': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'preco': np.random.uniform(10.0, 200.0, n_samples)
    }
    
    # Calculate target variable - risk level based on stock coverage
    # (estoque_atual / unidades_vendidas_90dias * 90) < vida_util_subsecao
    data['unidades_vendidas_90dias'] = data['unidades_vendidas_90dias'].clip(1)  # Avoid division by zero
    data['cobertura_estoque'] = data['estoque_atual'] / data['unidades_vendidas_90dias'] * 90
    data['risco_vencimento'] = np.where(
        data['cobertura_estoque'] > data['vida_util_subsecao'] * 1.5, 
        'alto', 
        np.where(
            data['cobertura_estoque'] > data['vida_util_subsecao'], 
            'medio', 
            'baixo'
        )
    )
    
    # Encode categorical variables
    data['secao_encoded'] = pd.Categorical(data['secao']).codes
    data['loja_encoded'] = pd.Categorical(data['cd_loja']).codes
    
    return pd.DataFrame(data)

def train_risk_model():
    """Train a model to predict product expiration risk"""
    logger.info("Training risk classification model...")
    
    try:
        # Fallback to simple processing
        df = generate_sample_data()
        
        # Features for the model
        features = [
            'vida_util_subsecao', 'unidades_vendidas_90dias', 'estoque_atual',
            'secao_encoded', 'cd_subsecao', 'loja_encoded', 'eh_sazonal', 'preco'
        ]
        
        X = df[features]
        y = pd.Categorical(df['risco_vencimento']).codes
        
        # Train a simple model (RandomForest for demo, could be XGBoost)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        logger.info("Risk model trained using fallback implementation")
        
        # Save the model
        joblib.dump(model, RISK_MODEL_PATH)
        logger.info(f"Risk model saved to {RISK_MODEL_PATH}")
        return True
    
    except Exception as e:
        logger.error(f"Error training risk model: {e}", exc_info=True)
        return False

def train_time_series_models():
    """Train time series models for sales velocity prediction"""
    logger.info("Training time series models...")
    
    try:
        # Here we're using RandomForest as a stand-in
        # In a real implementation, this would be Prophet or ARIMA models
        logger.info("Training simplified time series models...")
        
        # Create a dummy model that "predicts" sales velocity
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        # Train on random data (this is just a placeholder)
        X = np.random.rand(100, 3)
        y = np.random.choice([0, 1], 100)
        model.fit(X, y)
        
        # In a real implementation, we'd have multiple models for different product categories
        models = {
            'global': model,
            'categories': {
                'JARDIM': model,
                'PINTURA': model
            }
        }
        logger.info("Time series models trained using fallback implementation")
        
        # Save the models
        joblib.dump(models, TIME_SERIES_MODELS_PATH)
        logger.info(f"Time series models saved to {TIME_SERIES_MODELS_PATH}")
        return True
    
    except Exception as e:
        logger.error(f"Error training time series models: {e}", exc_info=True)
        return False

def main():
    """Main function to train all models"""
    logger.info("Starting model training process...")
    
    risk_success = train_risk_model()
    ts_success = train_time_series_models()
    
    if risk_success and ts_success:
        logger.info("All models trained and saved successfully")
        return 0
    else:
        logger.error("Failed to train one or more models")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 