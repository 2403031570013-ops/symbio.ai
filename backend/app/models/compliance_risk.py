from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from beanie import Document
from pydantic import Field


class ComplianceCheck(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    check_type: str
    regulation: str
    jurisdiction: str
    status: str = Field(default="pending")
    compliance_score: Optional[float] = Field(default=None)
    last_audit_date: Optional[datetime] = Field(default=None)
    next_audit_date: Optional[datetime] = Field(default=None)
    findings: Optional[Dict[str, Any]] = Field(default=None)
    corrective_actions: Optional[Dict[str, Any]] = Field(default=None)
    deadline: Optional[datetime] = Field(default=None)
    priority: str = Field(default="medium")
    auditor_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "compliance_checks"


class RiskAssessment(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    risk_category: str
    risk_description: str
    likelihood: int
    impact: int
    risk_score: float
    risk_level: str
    mitigation_strategies: Optional[Dict[str, Any]] = Field(default=None)
    owner: str
    review_date: Optional[datetime] = Field(default=None)
    status: str = Field(default="open")
    residual_risk: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "risk_assessments"


class AuditTrail(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    entity_type: str
    entity_id: str
    action: str
    user_id: str
    user_role: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None)
    changes: Optional[Dict[str, Any]] = Field(default=None)
    reason: Optional[str] = Field(default=None)
    custom_metadata: Optional[Dict[str, Any]] = Field(default=None)

    class Settings:
        collection = "audit_trails"


class DocumentCompliance(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    document_type: str
    document_name: str
    document_number: Optional[str] = Field(default=None)
    issuing_authority: str
    issue_date: datetime
    expiry_date: datetime
    status: str = Field(default="active")
    document_url: Optional[str] = Field(default=None)
    reminder_days: int = Field(default=30)
    last_verified: Optional[datetime] = Field(default=None)
    compliance_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "document_compliances"


class FraudDetection(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    entity_type: str
    entity_id: str
    detection_type: str
    risk_score: float
    confidence: float
    indicators: Optional[Dict[str, Any]] = Field(default=None)
    status: str = Field(default="flagged")
    investigation_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "fraud_detections"


class RegulatoryUpdate(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    regulation_name: str
    jurisdiction: str
    effective_date: datetime
    compliance_deadline: datetime
    description: str
    impact_level: str
    affected_industries: Optional[list[str]] = Field(default=None)
    requirements: Optional[list[str]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "regulatory_updates"
