from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class DynamicPricing(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    base_price: float
    current_price: float
    price_change: float
    demand_factor: float
    supply_factor: float
    competitor_pricing: Optional[Dict[str, Any]] = Field(default=None)
    seasonality_factor: Optional[float] = Field(default=None)
    urgency_factor: Optional[float] = Field(default=None)
    algorithm: str
    confidence_score: float
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    effective_until: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "dynamic_pricings"


class SmartNotification(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    notification_type: str
    title: str
    message: str
    priority: str = Field(default="normal")
    status: str = Field(default="unread")
    action_required: bool = Field(default=False)
    action_url: Optional[str] = Field(default=None)
    action_deadline: Optional[datetime] = Field(default=None)
    custom_metadata: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)

    class Settings:
        collection = "smart_notifications"


class WorkflowAutomation(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    description: Optional[str] = Field(default=None)
    trigger_type: str
    trigger_conditions: Optional[Dict[str, Any]] = Field(default=None)
    actions: Dict[str, Any]
    enabled: bool = Field(default=True)
    execution_count: int = Field(default=0)
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    last_executed: Optional[datetime] = Field(default=None)
    next_execution: Optional[datetime] = Field(default=None)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "workflow_automations"


class Contract(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    contract_number: Indexed(str, unique=True)
    contract_type: str
    party_a_id: str
    party_b_id: str
    material_id: Optional[str] = Field(default=None)
    start_date: datetime
    end_date: datetime
    value: float
    currency: str = Field(default="USD")
    terms: Optional[str] = Field(default=None)
    status: str = Field(default="draft")
    renewal_option: bool = Field(default=False)
    auto_renew: bool = Field(default=False)
    document_url: Optional[str] = Field(default=None)
    signed_by_party_a: bool = Field(default=False)
    signed_by_party_b: bool = Field(default=False)
    signed_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "contracts"


class Payment(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    contract_id: Optional[str] = Field(default=None)
    transaction_id: Optional[str] = Field(default=None)
    amount: float
    currency: str = Field(default="USD")
    payment_method: str
    status: str = Field(default="pending")
    payment_date: Optional[datetime] = Field(default=None)
    due_date: datetime
    paid_by: str
    paid_to: str
    reference_number: Optional[str] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None)
    transaction_fee: Optional[float] = Field(default=None)
    tax_amount: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "payments"


class BusinessIntelligence(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    report_type: str
    report_name: str
    period: str
    start_date: datetime
    end_date: datetime
    metrics: Optional[Dict[str, Any]] = Field(default=None)
    insights: Optional[Dict[str, Any]] = Field(default=None)
    trends: Optional[Dict[str, Any]] = Field(default=None)
    comparisons: Optional[Dict[str, Any]] = Field(default=None)
    recommendations: Optional[Dict[str, Any]] = Field(default=None)
    data_sources: Optional[Dict[str, Any]] = Field(default=None)
    generated_by: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "business_intelligence"


class AnomalyDetection(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    entity_type: str
    entity_id: str
    anomaly_type: str
    severity: str
    anomaly_score: float
    expected_value: float
    actual_value: float
    deviation_percentage: float
    context: Optional[Dict[str, Any]] = Field(default=None)
    detection_method: str
    status: str = Field(default="flagged")
    resolution: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)

    class Settings:
        collection = "anomaly_detections"


class PredictiveMaintenance(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    equipment_id: str
    equipment_name: str
    equipment_type: str
    health_score: float
    predicted_failure_date: Optional[datetime] = Field(default=None)
    confidence: float
    risk_level: str
    recommended_actions: Optional[Dict[str, Any]] = Field(default=None)
    sensor_data: Optional[Dict[str, Any]] = Field(default=None)
    maintenance_scheduled: bool = Field(default=False)
    scheduled_date: Optional[datetime] = Field(default=None)
    last_maintenance: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "predictive_maintenances"
