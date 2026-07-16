from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class RouteOptimizationBase(BaseModel):
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
    optimization_algorithm: str
    route_coordinates: Optional[Dict[str, Any]] = None


class RouteOptimizationCreate(RouteOptimizationBase):
    pass


class RouteOptimizationResponse(RouteOptimizationBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryBase(BaseModel):
    factory_id: str
    material_id: str
    current_stock: float
    minimum_stock: float
    maximum_stock: float
    reorder_point: float
    reorder_quantity: float


class InventoryCreate(InventoryBase):
    pass


class InventoryResponse(InventoryBase):
    id: str
    stock_status: str
    last_restock_date: Optional[datetime] = None
    next_restock_date: Optional[datetime] = None
    turnover_rate: Optional[float] = None
    holding_cost: Optional[float] = None
    stockout_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplyChainVisibilityBase(BaseModel):
    material_id: str
    supply_chain_stage: str
    supplier_id: str
    location: str
    status: str
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    delay_reason: Optional[str] = None
    risk_level: str = "low"
    alternative_suppliers: Optional[Dict[str, Any]] = None
    tracking_number: Optional[str] = None


class SupplyChainVisibilityCreate(SupplyChainVisibilityBase):
    pass


class SupplyChainVisibilityResponse(SupplyChainVisibilityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
