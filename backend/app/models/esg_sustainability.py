from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    material_id = Column(String, nullable=True)
    emission_source = Column(String, nullable=False)  # production, transport, storage
    co2_emitted = Column(Float, nullable=False)  # in kg
    baseline_co2 = Column(Float, nullable=True)
    reduction_percentage = Column(Float, nullable=True)
    calculation_method = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ESGScore(Base):
    __tablename__ = "esg_scores"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False, unique=True)
    environmental_score = Column(Float, nullable=False)  # 0-100
    social_score = Column(Float, nullable=False)  # 0-100
    governance_score = Column(Float, nullable=False)  # 0-100
    overall_score = Column(Float, nullable=False)  # 0-100
    rating = Column(String, nullable=False)  # AAA, AA, A, BBB, BB, B, CCC
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    next_assessment_date = Column(DateTime(timezone=True), nullable=True)
    criteria = Column(JSON, nullable=True)  # detailed scoring criteria
    improvements = Column(JSON, nullable=True)  # suggested improvements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class SustainabilityDashboard(Base):
    __tablename__ = "sustainability_dashboards"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    total_waste_diverted = Column(Float, default=0.0)  # in kg
    total_co2_saved = Column(Float, default=0.0)  # in kg
    water_saved = Column(Float, default=0.0)  # in liters
    energy_saved = Column(Float, default=0.0)  # in kWh
    recycling_rate = Column(Float, default=0.0)  # percentage
    circular_economy_score = Column(Float, default=0.0)  # 0-100
    zero_waste_certified = Column(Boolean, default=False)
    green_certifications = Column(JSON, nullable=True)  # list of certifications
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class WasteImpact(Base):
    __tablename__ = "waste_impacts"

    id = Column(String, primary_key=True, index=True)
    material_id = Column(String, nullable=False)
    waste_type = Column(String, nullable=False)
    environmental_impact = Column(JSON, nullable=True)  # detailed impact analysis
    economic_value = Column(Float, nullable=False)  # potential value if recycled
    diversion_method = Column(String, nullable=False)  # recycling, upcycling, energy recovery
    impact_score = Column(Float, nullable=False)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GreenCertification(Base):
    __tablename__ = "green_certifications"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    certification_name = Column(String, nullable=False)
    certification_body = Column(String, nullable=False)
    certification_level = Column(String, nullable=True)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="active")  # active, expired, suspended, pending
    certificate_url = Column(String, nullable=True)
    audit_score = Column(Float, nullable=True)
    requirements = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"

    id = Column(String, primary_key=True, index=True)
    factory_id = Column(String, nullable=False)
    credit_amount = Column(Float, nullable=False)  # in tons CO2e
    credit_type = Column(String, nullable=False)  # avoidance, removal
    project_type = Column(String, nullable=False)
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    price_per_credit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    available_for_sale = Column(Boolean, default=True)
    buyer_id = Column(String, nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=True)
    vintage_year = Column(Integer, nullable=False)
    registry = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
