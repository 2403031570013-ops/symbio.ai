from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
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


@router.post("/dynamic-pricing", response_model=DynamicPricingResponse)
def create_dynamic_pricing(
    pricing: DynamicPricingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create dynamic pricing"""
    db_pricing = DynamicPricing(**pricing.dict())
    db.add(db_pricing)
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


@router.get("/dynamic-pricing/{material_id}", response_model=List[DynamicPricingResponse])
def get_dynamic_pricing(
    material_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dynamic pricing for a material"""
    pricing = db.query(DynamicPricing).filter(
        DynamicPricing.material_id == material_id
    ).order_by(DynamicPricing.created_at.desc()).all()
    return pricing


@router.post("/smart-notifications", response_model=SmartNotificationResponse)
def create_smart_notification(
    notification: SmartNotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create smart notification"""
    db_notification = SmartNotification(**notification.dict(), user_id=current_user.id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.get("/smart-notifications", response_model=List[SmartNotificationResponse])
def get_smart_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's smart notifications"""
    notifications = db.query(SmartNotification).filter(
        SmartNotification.user_id == current_user.id
    ).order_by(SmartNotification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications


@router.put("/smart-notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = db.query(SmartNotification).filter(
        SmartNotification.id == notification_id,
        SmartNotification.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "read"
    db.commit()
    return {"message": "Notification marked as read"}


@router.post("/workflow-automation", response_model=WorkflowAutomationResponse)
def create_workflow_automation(
    automation: WorkflowAutomationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create workflow automation"""
    db_automation = WorkflowAutomation(**automation.dict(), created_by=current_user.id)
    db.add(db_automation)
    db.commit()
    db.refresh(db_automation)
    return db_automation


@router.get("/workflow-automation", response_model=List[WorkflowAutomationResponse])
def get_workflow_automations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow automations"""
    automations = db.query(WorkflowAutomation).filter(
        WorkflowAutomation.created_by == current_user.id
    ).all()
    return automations


@router.post("/contracts", response_model=ContractResponse)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create contract"""
    db_contract = Contract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.get("/contracts/{factory_id}", response_model=List[ContractResponse])
def get_contracts(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get contracts for a factory"""
    contracts = db.query(Contract).filter(
        Contract.party_a_id == factory_id
    ).order_by(Contract.created_at.desc()).all()
    return contracts


@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create payment"""
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/payments/{factory_id}", response_model=List[PaymentResponse])
def get_payments(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payments for a factory"""
    payments = db.query(Payment).filter(
        (Payment.paid_by == factory_id) | (Payment.paid_to == factory_id)
    ).order_by(Payment.created_at.desc()).all()
    return payments


@router.get("/business-intelligence/{factory_id}")
def get_business_intelligence(
    factory_id: str,
    report_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get business intelligence reports"""
    reports = db.query(BusinessIntelligence).filter(
        BusinessIntelligence.report_type == report_type
    ).order_by(BusinessIntelligence.created_at.desc()).limit(10).all()
    return reports


@router.get("/anomaly-detections/{factory_id}")
def get_anomaly_detections(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get anomaly detections for a factory"""
    detections = db.query(AnomalyDetection).filter(
        AnomalyDetection.entity_id == factory_id
    ).order_by(AnomalyDetection.created_at.desc()).all()
    return detections


@router.get("/predictive-maintenance/{factory_id}")
def get_predictive_maintenance(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get predictive maintenance data for a factory"""
    maintenance = db.query(PredictiveMaintenance).filter(
        PredictiveMaintenance.factory_id == factory_id
    ).order_by(PredictiveMaintenance.updated_at.desc()).all()
    return maintenance
