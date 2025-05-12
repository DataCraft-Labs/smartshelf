from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models.db_models import (  
    Recommendation as DBRecommendation,
    RecommendationItem as DBRecommendationItem,
    InventoryItem as DBInventoryItem,
    Product as DBProduct,
    Category as DBCategory,
    Store as DBStore
)
from ..models.schemas import RecommendedAction
from ..models.predictor import predictor_service
import random
from sqlalchemy.sql import text

router = APIRouter()

@router.get("/recommendations", response_model=List[RecommendedAction])
async def get_recommendations(impact: Optional[str] = None, db: Session = Depends(get_db)):
    """Get AI-generated recommendations for store management"""
    model_status = predictor_service.get_model_status()
    
    query = db.query(DBRecommendation)
    
    if impact:
        query = query.filter(DBRecommendation.impact == impact)
    
    recommendations = query.order_by(DBRecommendation.created_at.desc()).all()
    
    result = []
    for rec in recommendations:
        recommendation = RecommendedAction(
            id=rec.id,
            title=rec.title,
            description=rec.description,
            impact=rec.impact,
            is_useful=rec.is_useful
        )
        
        if model_status["models_loaded"] and "ML" not in recommendation.title:
            recommendation.description += " (Recomendação baseada em modelo de ML)"
        
        result.append(recommendation)
    
    return result

@router.post("/recommendations/{recommendation_id}/feedback")
async def provide_feedback(recommendation_id: int, is_useful: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    """Provide feedback on a recommendation"""
    recommendation = db.query(DBRecommendation).filter(DBRecommendation.id == recommendation_id).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.is_useful = is_useful
    db.commit()
    
    return {"status": "success", "message": "Feedback received"}

@router.post("/recommendations/generate", response_model=RecommendedAction)
async def generate_recommendation(
    category: Optional[str] = Body(None), 
    store: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """Generate a new recommendation based on product category and store"""
    model_status = predictor_service.get_model_status()
    model_based = model_status["models_loaded"]
    
    category_id = None
    category_value = "todas categorias"
    if category:
        category_obj = db.query(DBCategory).filter(DBCategory.name == category).first()
        if category_obj:
            category_id = category_obj.id
            category_value = category_obj.name
    
    store_id = None
    store_value = "todas lojas"
    if store:
        store_obj = db.query(DBStore).filter(DBStore.name == store).first()
        if store_obj:
            store_id = store_obj.id
            store_value = store_obj.name
    
    expiring_products_query = """
        SELECT 
            p.name as product_name,
            c.name as category_name,
            s.name as store_name,
            (i.expiration_date - CURRENT_DATE) as days_until_expiry,
            i.quantity
        FROM 
            inventory_items i
            JOIN products p ON i.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            JOIN stores s ON i.store_id = s.id
        WHERE 
            (i.expiration_date - CURRENT_DATE) <= 15
    """
    
    params = {}
    if category_id:
        expiring_products_query += " AND p.category_id = :category_id"
        params["category_id"] = category_id
    
    if store_id:
        expiring_products_query += " AND i.store_id = :store_id"
        params["store_id"] = store_id
    
    expiring_products_query += " ORDER BY days_until_expiry ASC LIMIT 5"
    
    expiring_products = db.execute(text(expiring_products_query), params).fetchall()
    
    recommendation_templates = [
        "Aplicar desconto de {discount}% em produtos de {category} na loja {store}",
        "Transferir produtos de {category} da loja {store} para outras unidades com maior demanda",
        "Realizar campanha específica para {category} na loja {store}",
        "Treinar equipe da loja {store} para sugerir ativamente produtos de {category}",
        "Reposicionar produtos de {category} em áreas de maior visibilidade na loja {store}"
    ]
    
    if model_based:
        recommendation_templates.append(
            "Com base em análise preditiva, recomendamos {action} para produtos de {category} "
            "na loja {store} para reduzir o risco de perdas em {risk_reduction}%"
        )
    
    template = recommendation_templates[0]
    
    if expiring_products:
        first_product = dict(expiring_products[0]._mapping)
        days_left = first_product["days_until_expiry"]
        product_name = first_product["product_name"]
        
        if days_left <= 7:
            discount = 30
            template = recommendation_templates[0]
        elif days_left <= 10:
            discount = 20
            template = recommendation_templates[0]
        elif days_left <= 15:
            discount = 15
            template = recommendation_templates[3]
        
        if len(expiring_products) > 2:
            template = recommendation_templates[1]
    else:
        discount = 15
        template_index = min(len(recommendation_templates) - 1, 2)
        template = recommendation_templates[template_index]
    
    risk_reduction = 0
    if expiring_products:
        total_days = sum(dict(p._mapping)["days_until_expiry"] for p in expiring_products)
        avg_days = total_days / len(expiring_products)
        risk_reduction = min(round(100 - (avg_days * 5)), 45)
    else:
        risk_reduction = 20
    
    actions = ["redução de preço", "transferência", "campanha específica"]
    action_index = 0
    
    if expiring_products:
        if any(dict(p._mapping)["days_until_expiry"] <= 7 for p in expiring_products):
            action_index = 0
        elif len(expiring_products) > 2 and all(dict(p._mapping)["days_until_expiry"] > 10 for p in expiring_products):
            action_index = 1
        else:
            action_index = 2
    
    template_vars = {
        "category": category_value,
        "store": store_value,
        "discount": discount,
        "action": actions[action_index],
        "risk_reduction": risk_reduction
    }
    
    description = template.format(**template_vars)
    
    recommendation_type = ["promotion", "transfer", "display", "training"][min(action_index, 3)]
    
    if risk_reduction > 30:
        impact = "high"
    elif risk_reduction > 15:
        impact = "medium"
    else:
        impact = "low"
    
    new_recommendation = DBRecommendation(
        title=f"{'[ML] ' if model_based else ''}Nova Recomendação para {category_value}",
        description=description,
        recommendation_type=recommendation_type,
        impact=impact,
        is_useful=None,
        acted_upon=False
    )
    
    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)
    
    if expiring_products and (category_id or store_id):
        inventory_query = (
            db.query(DBInventoryItem)
            .join(DBProduct, DBInventoryItem.product_id == DBProduct.id)
        )
        
        conditions = []
        if category_id:
            conditions.append(DBProduct.category_id == category_id)
        if store_id:
            conditions.append(DBInventoryItem.store_id == store_id)
        
        if conditions:
            inventory_query = inventory_query.filter(*conditions)
        
        inventory_items = inventory_query.limit(3).all()
        
        for item in inventory_items:
            recommendation_item = DBRecommendationItem(
                recommendation_id=new_recommendation.id,
                inventory_item_id=item.id
            )
            db.add(recommendation_item)
        
        db.commit()
    
    return RecommendedAction(
        id=new_recommendation.id,
        title=new_recommendation.title,
        description=new_recommendation.description,
        impact=new_recommendation.impact,
        is_useful=new_recommendation.is_useful
    )

@router.get("/recommendations/model-status")
async def get_model_status():
    """Get the status of the recommendation model"""
    return predictor_service.get_model_status()

@router.post("/recommendations/reload-models")
async def reload_models():
    """Force reload the ML models"""
    success = predictor_service.reload_models()
    return {
        "success": success,
        "model_status": predictor_service.get_model_status()
    } 