import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from app.models.marketplace_operations import (
    DynamicPricing, SmartNotification, WorkflowAutomation,
    Contract, Payment, BusinessIntelligence, AnomalyDetection, PredictiveMaintenance
)
from app.schemas.marketplace_operations import (
    DynamicPricingCreate, DynamicPricingResponse,
    SmartNotificationCreate, SmartNotificationResponse,
    WorkflowAutomationCreate, WorkflowAutomationResponse,
    ContractCreate, ContractResponse,
    PaymentCreate, PaymentResponse
)
from app.core.security import get_current_user

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.post("/dynamic-pricing", response_model=DynamicPricingResponse)
def create_dynamic_pricing(
    pricing: DynamicPricingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create dynamic pricing"""
    db_pricing = DynamicPricing(**pricing.dict())
    _run(db_pricing.insert())
    return db_pricing


@router.get("/dynamic-pricing/{material_id}", response_model=List[DynamicPricingResponse])
def get_dynamic_pricing(
    material_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dynamic pricing for a material"""
    pricing = _run(DynamicPricing.find(DynamicPricing.material_id == material_id).sort(-DynamicPricing.created_at).to_list())
    return pricing


@router.post("/smart-notifications", response_model=SmartNotificationResponse)
def create_smart_notification(
    notification: SmartNotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create smart notification"""
    db_notification = SmartNotification(**notification.dict(), user_id=current_user.id)
    _run(db_notification.insert())
    return db_notification


@router.get("/smart-notifications", response_model=List[SmartNotificationResponse])
def get_smart_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's smart notifications"""
    notifications = _run(SmartNotification.find(SmartNotification.user_id == current_user.id).sort(-SmartNotification.created_at).skip(skip).limit(limit).to_list())
    return notifications


@router.put("/smart-notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = _run(SmartNotification.find_one(SmartNotification.id == notification_id, SmartNotification.user_id == current_user.id))
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "read"
    _run(notification.save())
    return {"message": "Notification marked as read"}


@router.post("/workflow-automation", response_model=WorkflowAutomationResponse)
def create_workflow_automation(
    automation: WorkflowAutomationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create workflow automation"""
    db_automation = WorkflowAutomation(**automation.dict(), created_by=current_user.id)
    _run(db_automation.insert())
    return db_automation


@router.get("/workflow-automation", response_model=List[WorkflowAutomationResponse])
def get_workflow_automations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow automations"""
    automations = _run(WorkflowAutomation.find(WorkflowAutomation.created_by == current_user.id).to_list())
    return automations


@router.post("/contracts", response_model=ContractResponse)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create contract"""
    db_contract = Contract(**contract.dict())
    _run(db_contract.insert())
    return db_contract


@router.get("/contracts/{factory_id}", response_model=List[ContractResponse])
def get_contracts(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get contracts for a factory"""
    contracts = _run(Contract.find(Contract.party_a_id == factory_id).sort(-Contract.created_at).to_list())
    return contracts


@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create payment"""
    db_payment = Payment(**payment.dict())
    _run(db_payment.insert())
    return db_payment


@router.get("/payments/{factory_id}", response_model=List[PaymentResponse])
def get_payments(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payments for a factory"""
    payments = _run(Payment.find((Payment.paid_by == factory_id) | (Payment.paid_to == factory_id)).sort(-Payment.created_at).to_list())
    return payments


@router.get("/business-intelligence/{factory_id}")
def get_business_intelligence(
    factory_id: str,
    report_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get business intelligence reports"""
    reports = _run(BusinessIntelligence.find(BusinessIntelligence.report_type == report_type).sort(-BusinessIntelligence.created_at).limit(10).to_list())
    return reports


@router.get("/anomaly-detections/{factory_id}")
def get_anomaly_detections(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get anomaly detections for a factory"""
    detections = _run(AnomalyDetection.find(AnomalyDetection.entity_id == factory_id).sort(-AnomalyDetection.created_at).to_list())
    return detections


@router.get("/predictive-maintenance/{factory_id}")
def get_predictive_maintenance(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get predictive maintenance data for a factory"""
    maintenance = _run(PredictiveMaintenance.find(PredictiveMaintenance.factory_id == factory_id).sort(-PredictiveMaintenance.updated_at).to_list())
    return maintenance
