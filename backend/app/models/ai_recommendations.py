from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    recommendation_type = Column(String, nullable=False)  # material, supplier, route, pricing
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False)
    expected_benefit = Column(JSON, nullable=True)  # {"cost_savings": 1000, "time_savings": 5}
    status = Column(String, default="pending")  # pending, accepted, rejected, implemented
    custom_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(String, primary_key=True, index=True)
    material_id = Column(String, nullable=False)
    prediction_period = Column(String, nullable=False)  # weekly, monthly, quarterly
    predicted_demand = Column(Float, nullable=False)
    confidence_interval = Column(JSON, nullable=True)  # {"lower": 100, "upper": 150}
    factors = Column(JSON, nullable=True)  # {"seasonality": 0.2, "trend": 0.1}
    model_version = Column(String, nullable=False)
    accuracy_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prediction_date = Column(DateTime(timezone=True), nullable=False)


class PriceForecast(Base):
    __tablename__ = "price_forecasts"

    id = Column(String, primary_key=True, index=True)
    material_id = Column(String, nullable=False)
    forecast_period = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    price_change_percent = Column(Float, nullable=False)
    trend = Column(String, nullable=False)  # increasing, decreasing, stable
    volatility = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    market_factors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True), nullable=False)
