import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
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

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.post("/compliance-check", response_model=ComplianceCheckResponse)
def create_compliance_check(
    check: ComplianceCheckCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create compliance check"""
    db_check = ComplianceCheck(**check.dict())
    _run(db_check.insert())
    return db_check


@router.get("/compliance-check/{factory_id}", response_model=List[ComplianceCheckResponse])
def get_compliance_checks(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get compliance checks for a factory"""
    checks = _run(ComplianceCheck.find(ComplianceCheck.factory_id == factory_id).sort(-ComplianceCheck.created_at).to_list())
    return checks


@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create risk assessment"""
    db_assessment = RiskAssessment(**assessment.dict())
    _run(db_assessment.insert())
    return db_assessment


@router.get("/risk-assessment/{factory_id}", response_model=List[RiskAssessmentResponse])
def get_risk_assessments(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get risk assessments for a factory"""
    assessments = _run(RiskAssessment.find(RiskAssessment.factory_id == factory_id).sort(-RiskAssessment.created_at).to_list())
    return assessments


@router.get("/audit-trail/{entity_type}/{entity_id}")
def get_audit_trail(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get audit trail for an entity"""
    trail = _run(AuditTrail.find(AuditTrail.entity_type == entity_type, AuditTrail.entity_id == entity_id).sort(-AuditTrail.timestamp).to_list())
    return trail


@router.post("/document-compliance", response_model=DocumentComplianceResponse)
def create_document_compliance(
    document: DocumentComplianceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create document compliance record"""
    db_document = DocumentCompliance(**document.dict())
    _run(db_document.insert())
    return db_document


@router.get("/document-compliance/{factory_id}", response_model=List[DocumentComplianceResponse])
def get_document_compliance(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get document compliance for a factory"""
    documents = _run(DocumentCompliance.find(DocumentCompliance.factory_id == factory_id).to_list())
    return documents


@router.get("/regulatory-updates")
def get_regulatory_updates(
    jurisdiction: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get regulatory updates"""
    query = _run(RegulatoryUpdate.find_all().to_list())
    if jurisdiction:
        query = [item for item in query if item.jurisdiction == jurisdiction]
    return sorted(query, key=lambda item: item.created_at, reverse=True)


@router.get("/fraud-detections/{factory_id}")
def get_fraud_detections(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get fraud detections for a factory"""
    detections = _run(FraudDetection.find(FraudDetection.entity_type == "factory", FraudDetection.entity_id == factory_id).sort(-FraudDetection.created_at).to_list())
    return detections
