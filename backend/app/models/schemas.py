from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union, Any, Dict
from datetime import datetime, date
from decimal import Decimal

# Base schemas

class StoreBase(BaseModel):
    name: str
    location: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    category_id: int
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Category
    
    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    product_id: int
    store_id: int
    quantity: int
    expiration_date: date
    manufacturing_date: Optional[date] = None
    purchase_date: Optional[date] = None
    batch_number: Optional[str] = None
    unit_price: Optional[Decimal] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItem(InventoryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventoryItemDetail(InventoryItem):
    product: Product
    store: Store
    days_until_expiry: int
    
    class Config:
        from_attributes = True

class TransferBase(BaseModel):
    source_store_id: int
    destination_store_id: int
    inventory_item_id: int
    quantity: int
    status: str = "pending"

class TransferCreate(TransferBase):
    pass

class Transfer(TransferBase):
    id: int
    transfer_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PromotionBase(BaseModel):
    name: str
    description: Optional[str] = None
    discount_percentage: Decimal
    start_date: datetime
    end_date: datetime
    store_id: Optional[int] = None
    category_id: Optional[int] = None
    active: bool = True

class PromotionCreate(PromotionBase):
    pass

class Promotion(PromotionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PromotionItemBase(BaseModel):
    promotion_id: int
    inventory_item_id: int

class PromotionItemCreate(PromotionItemBase):
    pass

class PromotionItem(PromotionItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    title: str
    description: str
    recommendation_type: str
    impact: str = "medium"

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: int
    is_useful: Optional[bool] = None
    created_at: datetime
    acted_upon: bool = False
    acted_upon_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RecommendationItemBase(BaseModel):
    recommendation_id: int
    inventory_item_id: int

class RecommendationItemCreate(RecommendationItemBase):
    pass

class RecommendationItem(RecommendationItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStatBase(BaseModel):
    date: date
    total_savings: Decimal = Decimal('0.0')
    active_promotions: int = 0
    transferred_products: int = 0
    products_on_alert: int = 0

class DashboardStatCreate(DashboardStatBase):
    pass

class DashboardStat(DashboardStatBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Response models

class ProductAlert(BaseModel):
    product: InventoryItemDetail
    alert_level: str  # "high", "medium", "low"
    recommended_action: str

class DashboardSummary(BaseModel):
    total_savings: float
    active_promotions: int
    transferred_products: int
    products_on_alert: int

class RecommendedAction(BaseModel):
    id: int
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    is_useful: Optional[bool] = None 