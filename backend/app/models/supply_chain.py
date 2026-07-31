from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from beanie import Document
from pydantic import Field


class RouteOptimization(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    shipment_id: str
    origin: str
    destination: str
    original_distance: float
    optimized_distance: float
    distance_saved: float
    original_time: float
    optimized_time: float
    time_saved: float
    original_cost: float
    optimized_cost: float
    cost_saved: float
    co2_saved: float
    route_coordinates: Optional[Dict[str, Any]] = Field(default=None)
    optimization_algorithm: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "route_optimizations"


class Inventory(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    material_id: str
    current_stock: float
    minimum_stock: float
    maximum_stock: float
    reorder_point: float
    reorder_quantity: float
    stock_status: str = Field(default="normal")
    last_restock_date: Optional[datetime] = Field(default=None)
    next_restock_date: Optional[datetime] = Field(default=None)
    turnover_rate: Optional[float] = Field(default=None)
    holding_cost: Optional[float] = Field(default=None)
    stockout_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "inventories"


class SupplyChainVisibility(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    supply_chain_stage: str
    supplier_id: str
    location: str
    status: str
    estimated_arrival: Optional[datetime] = Field(default=None)
    actual_arrival: Optional[datetime] = Field(default=None)
    delay_reason: Optional[str] = Field(default=None)
    risk_level: str = Field(default="low")
    alternative_suppliers: Optional[Dict[str, Any]] = Field(default=None)
    tracking_number: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "supply_chain_visibilities"


class ShipmentTracking(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    shipment_id: str
    current_location: str
    destination: str
    status: str
    estimated_delivery: datetime
    actual_delivery: Optional[datetime] = Field(default=None)
    carrier: str
    tracking_events: Optional[Dict[str, Any]] = Field(default=None)
    temperature: Optional[Dict[str, Any]] = Field(default=None)
    humidity: Optional[Dict[str, Any]] = Field(default=None)
    condition: str = Field(default="good")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "shipment_trackings"


class SupplierPerformance(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    supplier_id: str
    factory_id: str
    on_time_delivery_rate: float
    quality_score: float
    response_time: float
    price_competitiveness: float
    communication_score: float
    overall_score: float
    rating: str
    total_orders: int = Field(default=0)
    total_deliveries: int = Field(default=0)
    delayed_deliveries: int = Field(default=0)
    quality_issues: int = Field(default=0)
    assessment_period: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "supplier_performances"


class LogisticsCost(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    shipment_id: str
    cost_category: str
    base_cost: float
    fuel_surcharge: Optional[float] = Field(default=None)
    handling_fee: Optional[float] = Field(default=None)
    insurance_cost: Optional[float] = Field(default=None)
    total_cost: float
    cost_per_unit: float
    cost_per_km: Optional[float] = Field(default=None)
    currency: str = Field(default="USD")
    budget: Optional[float] = Field(default=None)
    variance: Optional[float] = Field(default=None)
    variance_percentage: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "logistics_costs"

