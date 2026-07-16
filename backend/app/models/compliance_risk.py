from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    check_type = Column(String, nullable=False)  # environmental, safety, quality, labor
    regulation = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, compliant, non_compliant, exempt
    compliance_score = Column(Float, nullable=True)  # 0-100
    last_audit_date = Column(DateTime(timezone=True), nullable=True)
    next_audit_date = Column(DateTime(timezone=True), nullable=True)
    findings = Column(JSON, nullable=True)  # list of findings
    corrective_actions = Column(JSON, nullable=True)  # list of required actions
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    auditor_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    risk_category = Column(String, nullable=False)  # operational, financial, environmental, regulatory
    risk_description = Column(Text, nullable=False)
    likelihood = Column(Integer, nullable=False)  # 1-5
    impact = Column(Integer, nullable=False)  # 1-5
    risk_score = Column(Float, nullable=False)  # likelihood * impact
    risk_level = Column(String, nullable=False)  # low, medium, high, extreme
    mitigation_strategies = Column(JSON, nullable=True)
    owner = Column(String, nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="open")  # open, mitigated, accepted, transferred
    residual_risk = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # material, factory, transaction, user
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # create, update, delete, view, export
    user_id = Column(String, nullable=False)
    user_role = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    changes = Column(JSON, nullable=True)  # before and after values
    reason = Column(Text, nullable=True)
    custom_metadata = Column(JSON, nullable=True)


class DocumentCompliance(Base):
    __tablename__ = "document_compliances"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # license, permit, certificate, report
    document_name = Column(String, nullable=False)
    document_number = Column(String, nullable=True)
    issuing_authority = Column(String, nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="active")  # active, expired, suspended, pending_renewal
    document_url = Column(String, nullable=True)
    reminder_days = Column(Integer, default=30)
    last_verified = Column(DateTime(timezone=True), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class RegulatoryUpdate(Base):
    __tablename__ = "regulatory_updates"

    id = Column(String, primary_key=True, index=True)
    regulation_name = Column(String, nullable=False)
    regulation_code = Column(String, nullable=True)
    jurisdiction = Column(String, nullable=False)
    effective_date = Column(DateTime(timezone=True), nullable=False)
    compliance_deadline = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=False)
    impact_level = Column(String, nullable=False)  # low, medium, high
    affected_industries = Column(JSON, nullable=True)
    requirements = Column(JSON, nullable=True)
    status = Column(String, default="upcoming")  # upcoming, active, amended, repealed
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class FraudDetection(Base):
    __tablename__ = "fraud_detections"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # transaction, user, factory, material
    entity_id = Column(String, nullable=False)
    detection_type = Column(String, nullable=False)  # price_manipulation, fake_material, identity_fraud
    risk_score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-100
    indicators = Column(JSON, nullable=True)  # list of fraud indicators
    status = Column(String, default="flagged")  # flagged, investigating, confirmed_false, confirmed_fraud
    investigation_notes = Column(Text, nullable=True)
    investigator_id = Column(String, nullable=True)
    action_taken = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
