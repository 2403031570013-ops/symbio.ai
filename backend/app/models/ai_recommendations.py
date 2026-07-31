from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from beanie import Document
from pydantic import Field


class AIRecommendation(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    recommendation_type: str
    title: str
    description: Optional[str] = Field(default=None)
    confidence_score: float
    expected_benefit: Optional[Dict[str, Any]] = Field(default=None)
    status: str = Field(default="pending")
    custom_metadata: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)

    class Settings:
        collection = "ai_recommendations"


class DemandPrediction(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    prediction_period: str
    predicted_demand: float
    confidence_interval: Optional[Dict[str, Any]] = Field(default=None)
    factors: Optional[Dict[str, Any]] = Field(default=None)
    model_version: str
    accuracy_score: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    prediction_date: datetime

    class Settings:
        collection = "demand_predictions"


class PriceForecast(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    forecast_period: str
    current_price: float
    predicted_price: float
    price_change_percent: float
    trend: str
    volatility: float
    confidence_score: float
    market_factors: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_date: datetime

    class Settings:
        collection = "price_forecasts"
