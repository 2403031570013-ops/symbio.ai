from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class DynamicPricingBase(BaseModel):
    material_id: str
    base_price: float
    current_price: float
    price_change: float
    demand_factor: float
    supply_factor: float
    competitor_pricing: Optional[Dict[str, Any]] = None
    seasonality_factor: Optional[float] = None
    urgency_factor: Optional[float] = None
    algorithm: str
    confidence_score: float
    effective_until: Optional[datetime] = None


class DynamicPricingCreate(DynamicPricingBase):
    pass


class DynamicPricingResponse(DynamicPricingBase):
    id: str
    effective_from: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SmartNotificationBase(BaseModel):
    notification_type: str
    title: str
    message: str
    priority: str = "normal"
    action_required: bool = False
    action_url: Optional[str] = None
    action_deadline: Optional[datetime] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class SmartNotificationCreate(SmartNotificationBase):
    pass


class SmartNotificationResponse(SmartNotificationBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowAutomationBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_conditions: Optional[Dict[str, Any]] = None
    actions: List[Dict[str, Any]]
    enabled: bool = True


class WorkflowAutomationCreate(WorkflowAutomationBase):
    pass


class WorkflowAutomationResponse(WorkflowAutomationBase):
    id: str
    execution_count: int
    success_count: int
    failure_count: int
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractBase(BaseModel):
    contract_number: str
    contract_type: str
    party_a_id: str
    party_b_id: str
    material_id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    value: float
    currency: str = "USD"
    terms: Optional[str] = None
    renewal_option: bool = False
    auto_renew: bool = False
    document_url: Optional[str] = None


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: str
    status: str
    signed_by_party_a: bool
    signed_by_party_b: bool
    signed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentBase(BaseModel):
    contract_id: Optional[str] = None
    transaction_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    payment_method: str
    due_date: datetime
    paid_by: str
    paid_to: str
    reference_number: Optional[str] = None
    invoice_number: Optional[str] = None
    transaction_fee: Optional[float] = None
    tax_amount: Optional[float] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: str
    status: str
    payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
