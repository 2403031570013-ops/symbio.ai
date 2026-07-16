from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class ComplianceCheckBase(BaseModel):
    factory_id: str
    check_type: str
    regulation: str
    jurisdiction: str
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None
    findings: Optional[List[Dict[str, Any]]] = None
    corrective_actions: Optional[List[Dict[str, Any]]] = None
    deadline: Optional[datetime] = None
    priority: str = "medium"
    auditor_id: Optional[str] = None


class ComplianceCheckCreate(ComplianceCheckBase):
    pass


class ComplianceCheckResponse(ComplianceCheckBase):
    id: str
    status: str
    compliance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentBase(BaseModel):
    factory_id: str
    risk_category: str
    risk_description: str
    likelihood: int
    impact: int
    risk_score: float
    risk_level: str
    mitigation_strategies: Optional[List[Dict[str, Any]]] = None
    owner: str
    review_date: Optional[datetime] = None
    status: str = "open"
    residual_risk: Optional[float] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    pass


class RiskAssessmentResponse(RiskAssessmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentComplianceBase(BaseModel):
    factory_id: str
    document_type: str
    document_name: str
    document_number: Optional[str] = None
    issuing_authority: str
    issue_date: datetime
    expiry_date: datetime
    document_url: Optional[str] = None
    reminder_days: int = 30
    last_verified: Optional[datetime] = None
    compliance_notes: Optional[str] = None


class DocumentComplianceCreate(DocumentComplianceBase):
    pass


class DocumentComplianceResponse(DocumentComplianceBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
