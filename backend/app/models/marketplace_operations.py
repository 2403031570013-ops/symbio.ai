from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class DynamicPricing(Base):
    __tablename__ = "dynamic_pricings"

    id = Column(String, primary_key=True, index=True)
    material_id = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    price_change = Column(Float, nullable=False)
    demand_factor = Column(Float, nullable=False)
    supply_factor = Column(Float, nullable=False)
    competitor_pricing = Column(JSON, nullable=True)
    seasonality_factor = Column(Float, nullable=True)
    urgency_factor = Column(Float, nullable=True)
    algorithm = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    effective_from = Column(DateTime(timezone=True), server_default=func.now())
    effective_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SmartNotification(Base):
    __tablename__ = "smart_notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)  # match, price_alert, compliance, system
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    status = Column(String, default="unread")  # unread, read, archived
    action_required = Column(Boolean, default=False)
    action_url = Column(String, nullable=True)
    action_deadline = Column(DateTime(timezone=True), nullable=True)
    custom_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)


class WorkflowAutomation(Base):
    __tablename__ = "workflow_automations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(String, nullable=False)  # material_added, match_created, deadline_approaching
    trigger_conditions = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=False)  # list of actions to execute
    enabled = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_executed = Column(DateTime(timezone=True), nullable=True)
    next_execution = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String, primary_key=True, index=True)
    contract_number = Column(String, nullable=False, unique=True)
    contract_type = Column(String, nullable=False)  # purchase, sale, service
    party_a_id = Column(String, nullable=False)  # factory_id
    party_b_id = Column(String, nullable=False)  # partner_id
    material_id = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    terms = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft, active, expired, terminated, completed
    renewal_option = Column(Boolean, default=False)
    auto_renew = Column(Boolean, default=False)
    document_url = Column(String, nullable=True)
    signed_by_party_a = Column(Boolean, default=False)
    signed_by_party_b = Column(Boolean, default=False)
    signed_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    contract_id = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String, nullable=False)  # bank_transfer, credit_card, crypto
    status = Column(String, default="pending")  # pending, processing, completed, failed, refunded
    payment_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_by = Column(String, nullable=False)
    paid_to = Column(String, nullable=False)
    reference_number = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    transaction_fee = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class BusinessIntelligence(Base):
    __tablename__ = "business_intelligence"

    id = Column(String, primary_key=True, index=True)
    report_type = Column(String, nullable=False)  # sales, operations, financial, sustainability
    report_name = Column(String, nullable=False)
    period = Column(String, nullable=False)  # daily, weekly, monthly, quarterly, yearly
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    metrics = Column(JSON, nullable=True)  # key performance indicators
    insights = Column(JSON, nullable=True)  # generated insights
    trends = Column(JSON, nullable=True)  # trend analysis
    comparisons = Column(JSON, nullable=True)  # period over period comparisons
    recommendations = Column(JSON, nullable=True)
    data_sources = Column(JSON, nullable=True)
    generated_by = Column(String, nullable=True)  # ai, manual
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnomalyDetection(Base):
    __tablename__ = "anomaly_detections"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # price, volume, behavior, pattern
    entity_id = Column(String, nullable=False)
    anomaly_type = Column(String, nullable=False)  # spike, drop, pattern_break, outlier
    severity = Column(String, nullable=False)  # low, medium, high, critical
    anomaly_score = Column(Float, nullable=False)  # 0-100
    expected_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    deviation_percentage = Column(Float, nullable=False)
    context = Column(JSON, nullable=True)
    detection_method = Column(String, nullable=False)
    status = Column(String, default="flagged")  # flagged, investigating, resolved, false_positive
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class PredictiveMaintenance(Base):
    __tablename__ = "predictive_maintenances"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    equipment_id = Column(String, nullable=False)
    equipment_name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    health_score = Column(Float, nullable=False)  # 0-100
    predicted_failure_date = Column(DateTime(timezone=True), nullable=True)
    confidence = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False)  # low, medium, high, critical
    recommended_actions = Column(JSON, nullable=True)
    sensor_data = Column(JSON, nullable=True)
    maintenance_scheduled = Column(Boolean, default=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
