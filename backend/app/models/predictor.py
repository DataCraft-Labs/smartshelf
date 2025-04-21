from typing import Dict, List, Any, Optional
import pandas as pd
import joblib
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the predictor model modules
try:
    from predictor.src.models.risk_classifier import treinar_modelo_risco
    from predictor.src.models.time_series import treinar_modelo_tempo_vencimento
    from predictor.src.models.recommender import (
        avaliar_risco_estoque, 
        prever_dias_para_acao, 
        determinar_acao
    )
    from predictor.src.data.preprocessing import preparar_dados
    PREDICTOR_AVAILABLE = True
    logger.info("Predictor package is available and imported successfully")
except ImportError as e:
    PREDICTOR_AVAILABLE = False
    logger.warning(f"Failed to import predictor package: {e}")

# Define both relative and absolute paths for model files
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "trained"
RISK_MODEL_PATH = MODELS_DIR / "risk_model.joblib"
TIME_SERIES_MODELS_PATH = MODELS_DIR / "time_series_models.joblib"

# Alternative absolute paths
ABSOLUTE_MODELS_DIR = Path("/app/backend/app/models/trained")
ABSOLUTE_RISK_MODEL_PATH = ABSOLUTE_MODELS_DIR / "risk_model.joblib"
ABSOLUTE_TIME_SERIES_MODELS_PATH = ABSOLUTE_MODELS_DIR / "time_series_models.joblib"

class PredictorService:
    """Service to handle ML predictions for product risk and recommendations"""
    
    def __init__(self):
        self.risk_model = None
        self.time_series_models = None
        self.is_loaded = False
        
        # Try to load the models if they exist
        self._load_models()
    
    def _load_models(self) -> bool:
        """Load models from disk if they exist"""
        
        # Log detailed path information
        logger.info(f"Attempting to load models from the following paths:")
        logger.info(f"Relative path - MODELS_DIR: {MODELS_DIR}")
        logger.info(f"Relative path - RISK_MODEL_PATH: {RISK_MODEL_PATH}")
        logger.info(f"Relative path - TIME_SERIES_MODELS_PATH: {TIME_SERIES_MODELS_PATH}")
        logger.info(f"Absolute path - ABSOLUTE_MODELS_DIR: {ABSOLUTE_MODELS_DIR}")
        logger.info(f"Absolute path - ABSOLUTE_RISK_MODEL_PATH: {ABSOLUTE_RISK_MODEL_PATH}")
        logger.info(f"Absolute path - ABSOLUTE_TIME_SERIES_MODELS_PATH: {ABSOLUTE_TIME_SERIES_MODELS_PATH}")
        
        try:
            # First try with relative paths
            if MODELS_DIR.exists():
                logger.info(f"Models directory found at: {MODELS_DIR}")
                
                if RISK_MODEL_PATH.exists():
                    logger.info(f"Loading risk model from: {RISK_MODEL_PATH}")
                    self.risk_model = joblib.load(RISK_MODEL_PATH)
                    logger.info("Risk model loaded successfully")
                
                if TIME_SERIES_MODELS_PATH.exists():
                    logger.info(f"Loading time series models from: {TIME_SERIES_MODELS_PATH}")
                    self.time_series_models = joblib.load(TIME_SERIES_MODELS_PATH)
                    logger.info("Time series models loaded successfully")
            
            # If relative paths didn't work, try absolute paths
            elif ABSOLUTE_MODELS_DIR.exists():
                logger.info(f"Models directory found at: {ABSOLUTE_MODELS_DIR}")
                
                if ABSOLUTE_RISK_MODEL_PATH.exists():
                    logger.info(f"Loading risk model from: {ABSOLUTE_RISK_MODEL_PATH}")
                    self.risk_model = joblib.load(ABSOLUTE_RISK_MODEL_PATH)
                    logger.info("Risk model loaded successfully")
                
                if ABSOLUTE_TIME_SERIES_MODELS_PATH.exists():
                    logger.info(f"Loading time series models from: {ABSOLUTE_TIME_SERIES_MODELS_PATH}")
                    self.time_series_models = joblib.load(ABSOLUTE_TIME_SERIES_MODELS_PATH)
                    logger.info("Time series models loaded successfully")
            
            self.is_loaded = self.risk_model is not None or self.time_series_models is not None
            
            if self.is_loaded:
                logger.info("At least one model loaded successfully")
            else:
                logger.warning("No models were loaded, models_loaded status is FALSE")
            
            return self.is_loaded
        
        except Exception as e:
            logger.error(f"Error loading models: {e}", exc_info=True)
            return False

    def reload_models(self) -> bool:
        """Attempt to reload models from disk"""
        logger.info("Attempting to reload models...")
        return self._load_models()
    
    def process_chat_query(self, message: str) -> Dict[str, Any]:
        """
        Process a chat query and return relevant prediction data
        This method will be used by the chat API to provide AI-powered responses
        """
        lower_message = message.lower()
        response_data = {"prediction_available": self.is_loaded}
        
        # Extract relevant insights based on message content
        if "vencimento" in lower_message:
            response_data["category"] = "vencimento"
            if self.is_loaded:
                # Here you would add actual predictions from the model
                response_data["at_risk_count"] = 27  # Replace with actual model prediction
        
        elif "estoque" in lower_message:
            response_data["category"] = "estoque"
            if self.is_loaded:
                # Add stock level predictions
                response_data["current_stock_status"] = "adequate"
        
        elif "promoção" in lower_message or "promocao" in lower_message:
            response_data["category"] = "promocao"
            if self.is_loaded:
                # Add promotion recommendations
                response_data["active_promotions"] = 12
        
        elif "transferência" in lower_message or "transferencia" in lower_message:
            response_data["category"] = "transferencia"
            if self.is_loaded:
                # Add transfer recommendations
                response_data["suggested_transfers"] = ["Jardins - Produtos de Jardim"]
        
        return response_data
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the current status of the prediction models"""
        return {
            "models_loaded": self.is_loaded,
            "risk_model_available": self.risk_model is not None,
            "time_series_models_available": self.time_series_models is not None,
            "predictor_package_available": PREDICTOR_AVAILABLE
        }

# Create a global instance of the predictor service
predictor_service = PredictorService() 