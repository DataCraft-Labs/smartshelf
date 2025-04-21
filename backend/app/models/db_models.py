from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional, List
from ..database import Base

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="store")
    source_transfers = relationship("Transfer", foreign_keys="Transfer.source_store_id", back_populates="source_store")
    destination_transfers = relationship("Transfer", foreign_keys="Transfer.destination_store_id", back_populates="destination_store")
    promotions = relationship("Promotion", back_populates="store")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")
    promotions = relationship("Promotion", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    manufacturing_date = Column(Date)
    expiration_date = Column(Date, nullable=False)
    purchase_date = Column(Date)
    batch_number = Column(String)
    unit_price = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    store = relationship("Store", back_populates="inventory_items")
    transfers = relationship("Transfer", back_populates="inventory_item")
    promotion_items = relationship("PromotionItem", back_populates="inventory_item")
    recommendation_items = relationship("RecommendationItem", back_populates="inventory_item")

class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    source_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    destination_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    transfer_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    source_store = relationship("Store", foreign_keys=[source_store_id], back_populates="source_transfers")
    destination_store = relationship("Store", foreign_keys=[destination_store_id], back_populates="destination_transfers")
    inventory_item = relationship("InventoryItem", back_populates="transfers")

class Promotion(Base):
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="promotions")
    category = relationship("Category", back_populates="promotions")
    promotion_items = relationship("PromotionItem", back_populates="promotion")

class PromotionItem(Base):
    __tablename__ = "promotion_items"
    
    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    promotion = relationship("Promotion", back_populates="promotion_items")
    inventory_item = relationship("InventoryItem", back_populates="promotion_items")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendation_type = Column(String, nullable=False)
    impact = Column(String, default="medium")
    is_useful = Column(Boolean, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acted_upon = Column(Boolean, default=False)
    acted_upon_at = Column(DateTime(timezone=True))
    
    # Relationships
    recommendation_items = relationship("RecommendationItem", back_populates="recommendation")

class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="recommendation_items")
    inventory_item = relationship("InventoryItem", back_populates="recommendation_items")

class DashboardStat(Base):
    __tablename__ = "dashboard_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    total_savings = Column(Numeric(12, 2), default=0)
    active_promotions = Column(Integer, default=0)
    transferred_products = Column(Integer, default=0)
    products_on_alert = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 