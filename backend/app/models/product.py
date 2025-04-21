from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union, Any
from datetime import datetime, timedelta
from enum import Enum
import random

class Category(str, Enum):
    PINTURA = "Pintura"
    JARDIM = "Jardim"
    ELETRICA = "Elétrica"
    HIDRAULICA = "Hidráulica"
    FERRAMENTAS = "Ferramentas"
    MATERIAIS = "Materiais de Construção"

class Store(str, Enum):
    VILA_MARIANA = "Vila Mariana"
    PINHEIROS = "Pinheiros"
    JARDINS = "Jardins"
    MOEMA = "Moema"
    SANTANA = "Santana"
    TATUAPE = "Tatuapé"
    IPIRANGA = "Ipiranga"
    MOOCA = "Mooca"

class Product(BaseModel):
    id: int
    name: str
    category: Any
    quantity: int
    store: Any
    days_until_expiry: int = Field(..., description="Days remaining until the product expires")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Tinta Acrílica Fosca",
                "category": "Pintura",
                "quantity": 45,
                "store": "Marginal Tietê",
                "days_until_expiry": 15,
            }
        }

class ProductAlert(BaseModel):
    product: Product
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

# Mock data generation
def generate_mock_products(num_products: int = 50) -> List[Product]:
    products = []
    product_names = [
        "Tinta Acrílica Fosca", "Verniz Marítimo", "Buquê Primavera", 
        "Suculenta", "Cola de contato", "Lâmpada LED", "Fita isolante",
        "Cimento Portland", "Serra Circular", "Adubo Orgânico", "Mangueira",
        "Chave de fenda", "Furadeira", "Lixa d'água", "Massa Corrida"
    ]
    
    for i in range(1, num_products + 1):
        product = Product(
            id=i,
            name=random.choice(product_names),
            category=random.choice(list(Category)),
            quantity=random.randint(5, 100),
            store=random.choice(list(Store)),
            days_until_expiry=random.randint(1, 60),
        )
        products.append(product)
    
    return products 