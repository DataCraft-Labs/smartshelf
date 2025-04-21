from typing import List, Dict, Any, Optional, Union
import os
import logging
from pydantic import BaseModel, Field
import json
from datetime import datetime, timedelta
import pandas as pd
import random
from dotenv import load_dotenv

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Import predictor service
from .predictor import predictor_service

# Try to quietly load from .env file without excessive logging
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, '../..'))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path=env_path, verbose=False)

# Mock database for product data until we have a real one
# This would be replaced with actual database queries in production
class MockDatabase:
    def __init__(self):
        self.products = self._generate_mock_products(100)
        self.stores = ["Morumbi", "Vila Mariana", "Pinheiros", "Ibirapuera", "Paulista"]
        self.categories = ["Tintas", "Ferramentas", "Madeiras", "Elétrica", "Hidráulica", "Jardim", "Decoração"]
    
    def _generate_mock_products(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock product data for testing"""
        products = []
        stores = ["Morumbi", "Vila Mariana", "Pinheiros", "Ibirapuera", "Paulista"]
        categories = ["Tintas", "Ferramentas", "Madeiras", "Elétrica", "Hidráulica", "Jardim", "Decoração"]
        
        for i in range(count):
            # Generate a random expiration date between today and 60 days from now
            days_to_expiry = random.randint(0, 60)
            expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).strftime("%Y-%m-%d")
            
            # Generate random stock level
            stock = random.randint(1, 50)
            
            # Generate random price
            price = round(random.uniform(5.0, 500.0), 2)
            
            # Create product
            product = {
                "id": i + 1,
                "name": f"Produto {i + 1}",
                "category": random.choice(categories),
                "store_location": random.choice(stores),
                "stock_quantity": stock,
                "expiry_date": expiry_date,
                "days_to_expiry": days_to_expiry,
                "price": price,
                "risk_level": "high" if days_to_expiry < 7 else ("medium" if days_to_expiry < 15 else "low")
            }
            products.append(product)
        
        return products
    
    def get_products(self, 
                   store: Optional[str] = None, 
                   category: Optional[str] = None,
                   risk_level: Optional[str] = None,
                   days_to_expiry_lt: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query products with optional filters"""
        filtered_products = self.products
        
        if store:
            filtered_products = [p for p in filtered_products if p["store_location"] == store]
        
        if category:
            filtered_products = [p for p in filtered_products if p["category"] == category]
        
        if risk_level:
            filtered_products = [p for p in filtered_products if p["risk_level"] == risk_level]
        
        if days_to_expiry_lt is not None:
            filtered_products = [p for p in filtered_products if p["days_to_expiry"] < days_to_expiry_lt]
        
        return filtered_products
    
    def get_stores(self) -> List[str]:
        """Get list of all stores"""
        return self.stores
    
    def get_categories(self) -> List[str]:
        """Get list of all product categories"""
        return self.categories
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about inventory"""
        total_products = len(self.products)
        products_at_risk = len([p for p in self.products if p["risk_level"] == "high"])
        products_expiring_soon = len([p for p in self.products if p["days_to_expiry"] < 15])
        avg_stock_by_store = {}
        
        for store in self.stores:
            store_products = [p for p in self.products if p["store_location"] == store]
            if store_products:
                avg_stock = sum(p["stock_quantity"] for p in store_products) / len(store_products)
                avg_stock_by_store[store] = round(avg_stock, 2)
        
        return {
            "total_products": total_products,
            "products_at_risk": products_at_risk,
            "products_expiring_soon": products_expiring_soon,
            "avg_stock_by_store": avg_stock_by_store
        }

# Initialize mock database
mock_db = MockDatabase()

# PydanticAI Models for SmartShelf - using regular Pydantic models
class ProductInfo(BaseModel):
    """Information about a product in inventory"""
    id: int = Field(..., description="Unique identifier for the product")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    store_location: str = Field(..., description="Store where the product is located")
    stock_quantity: int = Field(..., description="Quantity in stock")
    expiry_date: str = Field(..., description="Expiration date (YYYY-MM-DD)")
    days_to_expiry: int = Field(..., description="Days until expiration")
    price: float = Field(..., description="Current price")
    risk_level: str = Field(..., description="Risk level (high, medium, low) based on days to expiry")

class StoreInfo(BaseModel):
    """Information about a store location"""
    name: str = Field(..., description="Store name")
    product_count: int = Field(..., description="Number of products in this store")
    at_risk_count: int = Field(..., description="Number of high-risk products in this store")
    avg_stock: float = Field(..., description="Average stock quantity per product")

class InventorySummary(BaseModel):
    """Summary of inventory across all stores"""
    total_products: int = Field(..., description="Total number of products in inventory")
    products_at_risk: int = Field(..., description="Number of high-risk products")
    products_expiring_soon: int = Field(..., description="Number of products expiring within 15 days")
    stores: List[StoreInfo] = Field(..., description="Summary by store")

class RecommendationResult(BaseModel):
    """Recommendation for a product or group of products"""
    product_ids: List[int] = Field(..., description="List of product IDs this recommendation applies to")
    action_type: str = Field(..., description="Type of recommended action (discount, transfer, restock)")
    reason: str = Field(..., description="Reason for the recommendation")
    potential_savings: float = Field(..., description="Estimated potential savings in BRL")
    urgency: str = Field(..., description="How urgent is this recommendation (high, medium, low)")
    
class ProductQueryResult(BaseModel):
    """Result of a product query"""
    products: List[ProductInfo] = Field(..., description="List of products matching the query")
    count: int = Field(..., description="Number of products returned")
    total_count: int = Field(..., description="Total number of products returned")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")

# Helper function to convert Pydantic models to dictionaries
def pydantic_to_dict(obj):
    """Convert Pydantic models to dictionaries for JSON serialization"""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    elif isinstance(obj, list):
        return [pydantic_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: pydantic_to_dict(v) for k, v in obj.items()}
    else:
        return obj

# Define regular functions instead of using @get_ai_function decorator
def get_inventory_summary() -> Dict[str, Any]:
    """
    Get a summary of the current inventory status across all stores, 
    including counts of at-risk products and products expiring soon.
    """
    # Get basic stats
    stats = mock_db.get_summary_stats()
    
    # Get store-specific stats
    stores = []
    for store_name in mock_db.get_stores():
        store_products = mock_db.get_products(store=store_name)
        at_risk_products = [p for p in store_products if p["risk_level"] == "high"]
        
        avg_stock = 0
        if store_products:
            avg_stock = sum(p["stock_quantity"] for p in store_products) / len(store_products)
        
        # Create dictionary instead of StoreInfo object
        stores.append({
            "name": store_name,
            "product_count": len(store_products),
            "at_risk_count": len(at_risk_products),
            "avg_stock": round(avg_stock, 2)
        })
    
    # Return a dictionary instead of InventorySummary object
    return {
        "total_products": stats["total_products"],
        "products_at_risk": stats["products_at_risk"],
        "products_expiring_soon": stats["products_expiring_soon"],
        "stores": stores
    }

def query_products(
    store: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    days_to_expiry_lt: Optional[int] = None,
    sort_by: Optional[str] = None,  # New parameter for sorting
    limit: Optional[int] = None     # New parameter to limit results
) -> Dict[str, Any]:
    """
    Query products in inventory with optional filters by store, category, 
    risk level, or days to expiry less than a specified value.
    Can sort results and limit the number returned.
    """
    filters = {
        "store": store,
        "category": category,
        "risk_level": risk_level,
        "days_to_expiry_lt": days_to_expiry_lt,
        "sort_by": sort_by,
        "limit": limit
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Query products
    product_data = mock_db.get_products(
        store=store,
        category=category,
        risk_level=risk_level,
        days_to_expiry_lt=days_to_expiry_lt
    )
    
    # Sort results if requested
    if sort_by:
        if sort_by == "days_to_expiry":
            product_data = sorted(product_data, key=lambda p: p["days_to_expiry"])
        elif sort_by == "days_to_expiry_desc":
            product_data = sorted(product_data, key=lambda p: p["days_to_expiry"], reverse=True)
        elif sort_by == "price":
            product_data = sorted(product_data, key=lambda p: p["price"])
        elif sort_by == "price_desc":
            product_data = sorted(product_data, key=lambda p: p["price"], reverse=True)
        elif sort_by == "stock":
            product_data = sorted(product_data, key=lambda p: p["stock_quantity"])
        elif sort_by == "stock_desc":
            product_data = sorted(product_data, key=lambda p: p["stock_quantity"], reverse=True)
        elif sort_by == "risk":
            # Sort by risk (high, medium, low)
            risk_order = {"high": 0, "medium": 1, "low": 2}
            product_data = sorted(product_data, key=lambda p: risk_order.get(p["risk_level"], 3))
    
    # Apply limit if specified
    if limit and limit > 0:
        product_data = product_data[:limit]
    
    # Keep product data as dictionaries instead of converting to Pydantic objects
    products = product_data
    
    total_count = len(product_data)
    
    return {
        "products": products,
        "count": len(products),
        "total_count": total_count,
        "filters_applied": filters
    }

def get_product_recommendations(
    category: Optional[str] = None, 
    store: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get AI-powered recommendations for products that require attention.
    Optionally filter by category or store, and limit the number of results.
    Results are sorted by urgency (high to low) and potential savings (high to low).
    """
    # Get products that may need attention
    products = mock_db.get_products(
        store=store,
        category=category,
        days_to_expiry_lt=30  # Only products with less than 30 days to expiry
    )
    
    # Group products by category and store for bulk recommendations
    grouped_products = {}
    for p in products:
        key = f"{p['category']}_{p['store_location']}"
        if key not in grouped_products:
            grouped_products[key] = []
        grouped_products[key].append(p)
    
    recommendations = []
    
    # Generate recommendations for each group
    for group_key, group_products in grouped_products.items():
        # Only recommend for groups with at least one high-risk product
        high_risk_products = [p for p in group_products if p["risk_level"] == "high"]
        if high_risk_products:
            # Calculate potential savings (assume 40% of product value would be lost otherwise)
            total_value = sum(p["price"] * p["stock_quantity"] for p in high_risk_products)
            potential_savings = total_value * 0.4
            
            # Determine urgency based on days to expiry
            avg_days = sum(p["days_to_expiry"] for p in high_risk_products) / len(high_risk_products)
            urgency = "high" if avg_days < 7 else ("medium" if avg_days < 15 else "low")
            
            # Determine action type
            if len(high_risk_products) >= 5:
                action = "discount"
                reason = f"{len(high_risk_products)} products in {group_products[0]['category']} at {group_products[0]['store_location']} will expire soon"
            else:
                action = "transfer"
                reason = f"Low demand for these {len(high_risk_products)} products at current location"
                
            # Include product details in the recommendation
            product_details = []
            for p in high_risk_products:
                product_details.append({
                    "id": p["id"],
                    "name": p["name"],
                    "category": p["category"],
                    "days_to_expiry": p["days_to_expiry"],
                    "store_location": p["store_location"],
                    "price": p["price"],
                    "stock_quantity": p["stock_quantity"]
                })
            
            # Create result as dictionary directly instead of Pydantic model
            recommendations.append({
                "product_ids": [p["id"] for p in high_risk_products],
                "product_names": [p["name"] for p in high_risk_products],
                "product_details": product_details,
                "action_type": action,
                "category": group_products[0]["category"],
                "store_location": group_products[0]["store_location"],
                "reason": reason,
                "potential_savings": round(potential_savings, 2),
                "urgency": urgency,
                "urgency_level": 0 if urgency == "high" else (1 if urgency == "medium" else 2),  # For sorting
                "avg_days_to_expiry": round(avg_days, 1)
            })
    
    # Sort recommendations by urgency (high to low) and then by potential savings (high to low)
    recommendations.sort(key=lambda r: (r["urgency_level"], -r["potential_savings"]))
    
    # Limit results if specified
    if limit and limit > 0 and len(recommendations) > limit:
        recommendations = recommendations[:limit]
    
    return recommendations

def get_available_stores() -> List[str]:
    """Get a list of all store locations in the system"""
    return mock_db.get_stores()

def get_product_categories() -> List[str]:
    """Get a list of all product categories in the system"""
    return mock_db.get_categories()

def get_high_risk_products(
    limit: Optional[int] = None,
    store: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = "days_to_expiry"  # Default to sorting by days to expiry
) -> Dict[str, Any]:
    """
    Get products with high risk level, sorted by days to expiry by default.
    This is a dedicated function to find the most at-risk products.
    """
    # Query high-risk products
    product_data = mock_db.get_products(
        store=store,
        category=category,
        risk_level="high"
    )
    
    # Sort results (default is by days to expiry)
    if sort_by == "days_to_expiry":
        product_data = sorted(product_data, key=lambda p: p["days_to_expiry"])
    elif sort_by == "days_to_expiry_desc":
        product_data = sorted(product_data, key=lambda p: p["days_to_expiry"], reverse=True)
    elif sort_by == "financial_risk":
        # Sort by price * quantity for financial risk
        for p in product_data:
            p["financial_risk"] = p["price"] * p["stock_quantity"]
        product_data = sorted(product_data, key=lambda p: p["financial_risk"], reverse=True)
    
    # Apply limit if specified
    if limit and limit > 0:
        product_data = product_data[:limit]
    
    filters = {
        "risk_level": "high",
        "store": store,
        "category": category,
        "sort_by": sort_by,
        "limit": limit
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    return {
        "high_risk_products": product_data,
        "count": len(product_data),
        "filters_applied": filters
    }

# Manually define function specifications for OpenAI
def create_function_specs():
    """Create function specifications for OpenAI tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_inventory_summary",
                "description": "Get a summary of the current inventory status across all stores, including counts of at-risk products and products expiring soon.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_products",
                "description": "Query products in inventory with optional filters by store, category, risk level, or days to expiry less than a specified value. Can sort results and limit the number returned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "store": {
                            "type": "string",
                            "description": "Filter by store location"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by product category"
                        },
                        "risk_level": {
                            "type": "string",
                            "description": "Filter by risk level (high, medium, low)"
                        },
                        "days_to_expiry_lt": {
                            "type": "integer",
                            "description": "Filter by days to expiry less than this value"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort results by this attribute (days_to_expiry, days_to_expiry_desc, price, price_desc, stock, stock_desc, risk)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limit the number of results returned"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_recommendations",
                "description": "Get AI-powered recommendations for products that require attention. Optionally filter by category or store, and limit the number of results. Results are sorted by urgency (high to low) and potential savings (high to low).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by product category"
                        },
                        "store": {
                            "type": "string",
                            "description": "Filter by store location"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limit the number of results returned"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_available_stores",
                "description": "Get a list of all store locations in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_categories",
                "description": "Get a list of all product categories in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_high_risk_products",
                "description": "Get products with high risk level, sorted by days to expiry by default. This is a dedicated function to find the most at-risk products.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Limit the number of results returned"
                        },
                        "store": {
                            "type": "string",
                            "description": "Filter by store location"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by product category"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort results by this attribute (days_to_expiry, days_to_expiry_desc, financial_risk)"
                        }
                    },
                    "required": []
                }
            }
        }
    ]

# Agentic Service class
class AgenticService:
    """Service to handle agentic interactions using OpenAI function calling"""
    
    def __init__(self):
        self.available_functions = {
            "get_inventory_summary": get_inventory_summary,
            "query_products": query_products, 
            "get_product_recommendations": get_product_recommendations,
            "get_available_stores": get_available_stores,
            "get_product_categories": get_product_categories,
            "get_high_risk_products": get_high_risk_products
        }
        
        # Create function specs for OpenAI
        self.function_specs = create_function_specs()
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a chat message using agentic capabilities
        Returns a structured response containing valuable information
        """
        try:
            # Import libraries only when needed to handle cases where OpenAI is not installed
            from openai import OpenAI
            
            # Reload environment variables right before using them
            load_dotenv(dotenv_path=env_path, override=True, verbose=False)
            
            # Get the API key from environment - don't override it if it already exists
            api_key = os.environ.get("OPENAI_API_KEY")
            
            # Quietly check API key availability
            if not api_key or api_key == "your-openai-api-key-here":
                return {
                    "error": "OpenAI API key not configured",
                    "message": "The OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
                }
            
            # Initialize OpenAI client with the API key from environment
            client = OpenAI(api_key=api_key)
            
            # First, ask the model what function it would like to call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a more widely available model
                messages=[
                    {"role": "system", "content": "You are an AI assistant for SmartShelf, an intelligent product management system for tracking perishable products. CRITICAL INSTRUCTION: You must ONLY provide information returned directly by the function calls. DO NOT make up or hallucinate any product IDs, statistics, or data. When asked for specific products, you MUST first call a function to retrieve the actual data. If a user asks about 'highest risk' products, you MUST query products with risk_level='high' and sort by days_to_expiry. NEVER mention specific product information unless it was explicitly returned in your function call results."},
                    {"role": "user", "content": message}
                ],
                tools=self.function_specs,
                tool_choice="auto"
            )
            
            # Extract the response
            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.tool_calls:
                # Prepare to collect function results
                function_results = []
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the function
                    if function_name in self.available_functions:
                        function_result = self.available_functions[function_name](**function_args)
                        
                        # Use our helper to convert Pydantic models to dictionaries
                        result_dict = pydantic_to_dict(function_result)
                        
                        function_results.append({
                            "name": function_name,
                            "arguments": function_args,
                            "result": result_dict
                        })
                
                # Now get a final response from the model with the function results
                messages = [
                    {"role": "system", "content": "You are an AI assistant for SmartShelf, an intelligent product management system for tracking perishable products. CRITICAL INSTRUCTION: You must ONLY respond with information that appears EXACTLY in the function results. DO NOT invent any data or details. When discussing products, you must only mention the specific products returned by your function calls. If you're asked about high-risk products, ONLY include products that have risk_level='high' in the data. If the function didn't return certain information, acknowledge that the information is not available. Always double-check that every product ID, name, stat, or detail you provide exists in the function results."},
                    {"role": "user", "content": message}
                ]
                
                # Add the original response and function results
                messages.append({"role": "assistant", "content": None, "tool_calls": response_message.tool_calls})
                
                # Add function results
                for idx, tool_call in enumerate(response_message.tool_calls):
                    result = function_results[idx]["result"]
                    # Serialize the result to JSON
                    serialized_result = json.dumps(result)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": serialized_result
                    })
                
                # Get the final response
                final_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using a more widely available model
                    messages=messages
                )
                
                return {
                    "response": final_response.choices[0].message.content,
                    "function_calls": function_results
                }
            else:
                # If no function was called, just return the response content
                return {
                    "response": response_message.content,
                    "function_calls": []
                }
                
        except Exception as e:
            logger.error(f"Error in agentic processing: {e}")
            return {
                "error": str(e),
                "message": "An error occurred while processing your request."
            }

# Create a global instance of the agentic service
agentic_service = AgenticService() 