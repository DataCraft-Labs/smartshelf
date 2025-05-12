from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from ..models.predictor import predictor_service
from ..models.agentic import agentic_service

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    use_agentic: Optional[bool] = True  # Default to using agentic processing

class ChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]
    prediction_data: Optional[Dict[str, Any]] = None
    function_calls: Optional[List[Dict[str, Any]]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI assistant"""
    user_message = request.message
    history = request.history if request.history else []
    
    # Add user message to history
    history.append(ChatMessage(role="user", content=request.message))
    
    # Try using the agentic service if enabled
    if request.use_agentic:
        try:
            # Process the message using the agentic service
            agentic_result = agentic_service.process_message(user_message)
            
            # Check if we got a valid response or an error
            if "error" not in agentic_result:
                # Add assistant response to history
                response = agentic_result["response"]
                history.append(ChatMessage(role="assistant", content=response))
                
                return ChatResponse(
                    response=response, 
                    history=history, 
                    function_calls=agentic_result.get("function_calls")
                )
            else:
                # Log the error and provide a simple fallback response
                logger.warning(f"Agentic processing error: {agentic_result['error']}")
                response = "I'm sorry, but the AI chat assistant is currently unavailable. Please make sure the OpenAI API key is properly configured."
        except Exception as e:
            # If any exception occurs, provide a simple fallback response
            logger.error(f"Error in agentic processing: {e}")
            response = "I'm sorry, but an error occurred while processing your request. Please try again later."
    else:
        # If agentic processing is disabled, provide a simple response
        response = "Hello! I'm the SmartShelf assistant. I can help you manage your inventory, track expiring products, and provide recommendations. To use my advanced features, please make sure the AI services are enabled."
    
    # Add assistant response to history
    history.append(ChatMessage(role="assistant", content=response))
    
    return ChatResponse(response=response, history=history)

@router.get("/chat/model-status")
async def get_model_status():
    """Get the status of the prediction models"""
    return predictor_service.get_model_status()

@router.get("/chat/agentic-status")
async def get_agentic_status():
    """Get the status of the agentic capabilities"""
    try:
        # Import here to avoid failing if not installed
        from openai import OpenAI
        import os
        
        api_key = os.environ.get("OPENAI_API_KEY", "")
        has_api_key = bool(api_key and api_key != "your-openai-api-key-here")
        
        # Check if the API key is valid by making a small test request
        if has_api_key:
            try:
                client = OpenAI(api_key=api_key)
                # Make a minimal API call to check if the key works
                client.models.list(limit=1)
                key_valid = True
            except Exception as e:
                key_valid = False
                api_error = str(e)
        else:
            key_valid = False
            api_error = "No API key provided"
        
        return {
            "agentic_available": True,
            "openai_available": True,
            "has_api_key": has_api_key,
            "key_valid": key_valid,
            "api_error": api_error if not key_valid and has_api_key else None,
            "available_functions": list(agentic_service.available_functions.keys())
        }
    except ImportError:
        return {
            "agentic_available": False,
            "error": "OpenAI Python package not installed"
        } 
