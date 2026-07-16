from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class AIRecommendationBase(BaseModel):
    recommendation_type: str
    title: str
    description: Optional[str] = None
    confidence_score: float
    expected_benefit: Optional[Dict[str, Any]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class AIRecommendationCreate(AIRecommendationBase):
    pass


class AIRecommendationResponse(AIRecommendationBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DemandPredictionBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    material_id: str
    prediction_period: str
    predicted_demand: float
    confidence_interval: Optional[Dict[str, float]] = None
    factors: Optional[Dict[str, float]] = None
    model_version: str
    prediction_date: datetime


class DemandPredictionCreate(DemandPredictionBase):
    pass


class DemandPredictionResponse(DemandPredictionBase):
    id: str
    accuracy_score: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceForecastBase(BaseModel):
    material_id: str
    forecast_period: str
    current_price: float
    predicted_price: float
    price_change_percent: float
    trend: str
    volatility: float
    confidence_score: float
    market_factors: Optional[Dict[str, Any]] = None
    target_date: datetime


class PriceForecastCreate(PriceForecastBase):
    pass


class PriceForecastResponse(PriceForecastBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
