from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.compliance_risk import (
    ComplianceCheck, RiskAssessment, AuditTrail,
    DocumentCompliance, RegulatoryUpdate, FraudDetection
)
from app.schemas.compliance_risk import (
    ComplianceCheckCreate, ComplianceCheckResponse,
    RiskAssessmentCreate, RiskAssessmentResponse,
    DocumentComplianceCreate, DocumentComplianceResponse
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/compliance-check", response_model=ComplianceCheckResponse)
def create_compliance_check(
    check: ComplianceCheckCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create compliance check"""
    db_check = ComplianceCheck(**check.dict())
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


@router.get("/compliance-check/{factory_id}", response_model=List[ComplianceCheckResponse])
def get_compliance_checks(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get compliance checks for a factory"""
    checks = db.query(ComplianceCheck).filter(
        ComplianceCheck.factory_id == factory_id
    ).order_by(ComplianceCheck.created_at.desc()).all()
    return checks


@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create risk assessment"""
    db_assessment = RiskAssessment(**assessment.dict())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.get("/risk-assessment/{factory_id}", response_model=List[RiskAssessmentResponse])
def get_risk_assessments(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get risk assessments for a factory"""
    assessments = db.query(RiskAssessment).filter(
        RiskAssessment.factory_id == factory_id
    ).order_by(RiskAssessment.created_at.desc()).all()
    return assessments


@router.get("/audit-trail/{entity_type}/{entity_id}")
def get_audit_trail(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get audit trail for an entity"""
    trail = db.query(AuditTrail).filter(
        AuditTrail.entity_type == entity_type,
        AuditTrail.entity_id == entity_id
    ).order_by(AuditTrail.timestamp.desc()).all()
    return trail


@router.post("/document-compliance", response_model=DocumentComplianceResponse)
def create_document_compliance(
    document: DocumentComplianceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create document compliance record"""
    db_document = DocumentCompliance(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/document-compliance/{factory_id}", response_model=List[DocumentComplianceResponse])
def get_document_compliance(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get document compliance for a factory"""
    documents = db.query(DocumentCompliance).filter(
        DocumentCompliance.factory_id == factory_id
    ).all()
    return documents


@router.get("/regulatory-updates")
def get_regulatory_updates(
    jurisdiction: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get regulatory updates"""
    query = db.query(RegulatoryUpdate)
    if jurisdiction:
        query = query.filter(RegulatoryUpdate.jurisdiction == jurisdiction)
    updates = query.order_by(RegulatoryUpdate.created_at.desc()).all()
    return updates


@router.get("/fraud-detections/{factory_id}")
def get_fraud_detections(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get fraud detections for a factory"""
    detections = db.query(FraudDetection).filter(
        FraudDetection.entity_type == "factory",
        FraudDetection.entity_id == factory_id
    ).order_by(FraudDetection.created_at.desc()).all()
    return detections
