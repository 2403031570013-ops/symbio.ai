from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field


class CarbonFootprint(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    material_id: Optional[str] = Field(default=None)
    emission_source: str
    co2_emitted: float
    baseline_co2: Optional[float] = Field(default=None)
    reduction_percentage: Optional[float] = Field(default=None)
    calculation_method: str
    verified: bool = Field(default=False)
    verification_date: Optional[datetime] = Field(default=None)
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "carbon_footprints"


class ESGScore(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: Indexed(str, unique=True)
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    rating: str
    assessment_date: datetime
    next_assessment_date: Optional[datetime] = Field(default=None)
    criteria: Optional[Dict[str, Any]] = Field(default=None)
    improvements: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "esg_scores"


class SustainabilityDashboard(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    total_waste_diverted: float = Field(default=0.0)
    total_co2_saved: float = Field(default=0.0)
    water_saved: float = Field(default=0.0)
    energy_saved: float = Field(default=0.0)
    recycling_rate: float = Field(default=0.0)
    circular_economy_score: float = Field(default=0.0)
    zero_waste_certified: bool = Field(default=False)
    green_certifications: Optional[Dict[str, Any]] = Field(default=None)
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "sustainability_dashboards"


class WasteImpact(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    material_id: str
    waste_type: str
    environmental_impact: Optional[Dict[str, Any]] = Field(default=None)
    economic_value: float
    diversion_method: str
    impact_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "waste_impacts"


class GreenCertification(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    certification_name: str
    certification_body: str
    certification_level: Optional[str] = Field(default=None)
    issue_date: datetime
    expiry_date: datetime
    status: str = Field(default="active")
    certificate_url: Optional[str] = Field(default=None)
    audit_score: Optional[float] = Field(default=None)
    requirements: Optional[Dict[str, Any]] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "green_certifications"


class CarbonCredit(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    factory_id: str
    credit_amount: float
    credit_type: str
    project_type: str
    verification_status: str = Field(default="pending")
    price_per_credit: float
    total_value: float
    available_for_sale: bool = Field(default=True)
    buyer_id: Optional[str] = Field(default=None)
    transaction_date: Optional[datetime] = Field(default=None)
    vintage_year: int
    registry: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "carbon_credits"
