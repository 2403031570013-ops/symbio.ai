from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class RouteOptimization(Base):
    __tablename__ = "route_optimizations"

    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    original_distance = Column(Float, nullable=False)  # in km
    optimized_distance = Column(Float, nullable=False)  # in km
    distance_saved = Column(Float, nullable=False)  # in km
    original_time = Column(Float, nullable=False)  # in hours
    optimized_time = Column(Float, nullable=False)  # in hours
    time_saved = Column(Float, nullable=False)  # in hours
    original_cost = Column(Float, nullable=False)
    optimized_cost = Column(Float, nullable=False)
    cost_saved = Column(Float, nullable=False)
    co2_saved = Column(Float, nullable=False)  # in kg
    route_coordinates = Column(JSON, nullable=True)
    optimization_algorithm = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    material_id = Column(String, nullable=False)
    current_stock = Column(Float, nullable=False)
    minimum_stock = Column(Float, nullable=False)
    maximum_stock = Column(Float, nullable=False)
    reorder_point = Column(Float, nullable=False)
    reorder_quantity = Column(Float, nullable=False)
    stock_status = Column(String, default="normal")  # normal, low, critical, overstocked
    last_restock_date = Column(DateTime(timezone=True), nullable=True)
    next_restock_date = Column(DateTime(timezone=True), nullable=True)
    turnover_rate = Column(Float, nullable=True)
    holding_cost = Column(Float, nullable=True)
    stockout_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class SupplyChainVisibility(Base):
    __tablename__ = "supply_chain_visibilities"

    id = Column(String, primary_key=True, index=True)
    material_id = Column(String, nullable=False)
    supply_chain_stage = Column(String, nullable=False)  # raw_material, manufacturing, distribution, retail
    supplier_id = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)  # active, delayed, blocked, completed
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    delay_reason = Column(Text, nullable=True)
    risk_level = Column(String, default="low")  # low, medium, high, critical
    alternative_suppliers = Column(JSON, nullable=True)
    tracking_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class ShipmentTracking(Base):
    __tablename__ = "shipment_trackings"

    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, nullable=False)
    current_location = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(String, nullable=False)  # in_transit, delivered, delayed, cancelled
    estimated_delivery = Column(DateTime(timezone=True), nullable=False)
    actual_delivery = Column(DateTime(timezone=True), nullable=True)
    carrier = Column(String, nullable=False)
    tracking_events = Column(JSON, nullable=True)  # list of tracking events
    temperature = Column(JSON, nullable=True)  # for sensitive materials
    humidity = Column(JSON, nullable=True)
    condition = Column(String, default="good")  # good, damaged, spoiled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class SupplierPerformance(Base):
    __tablename__ = "supplier_performances"

    id = Column(String, primary_key=True, index=True)
    supplier_id = Column(String, nullable=False)
    factory_id = Column(String, nullable=False)
    on_time_delivery_rate = Column(Float, nullable=False)  # percentage
    quality_score = Column(Float, nullable=False)  # 0-100
    response_time = Column(Float, nullable=False)  # in hours
    price_competitiveness = Column(Float, nullable=False)  # 0-100
    communication_score = Column(Float, nullable=False)  # 0-100
    overall_score = Column(Float, nullable=False)  # 0-100
    rating = Column(String, nullable=False)  # excellent, good, average, poor
    total_orders = Column(Integer, default=0)
    total_deliveries = Column(Integer, default=0)
    delayed_deliveries = Column(Integer, default=0)
    quality_issues = Column(Integer, default=0)
    assessment_period = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class LogisticsCost(Base):
    __tablename__ = "logistics_costs"

    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, nullable=False)
    cost_category = Column(String, nullable=False)  # transportation, storage, handling, insurance
    base_cost = Column(Float, nullable=False)
    fuel_surcharge = Column(Float, nullable=True)
    handling_fee = Column(Float, nullable=True)
    insurance_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=False)
    cost_per_unit = Column(Float, nullable=False)
    cost_per_km = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    budget = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    variance_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
