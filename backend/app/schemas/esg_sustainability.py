from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class CarbonFootprintBase(BaseModel):
    factory_id: str
    material_id: Optional[str] = None
    emission_source: str
    co2_emitted: float
    baseline_co2: Optional[float] = None
    reduction_percentage: Optional[float] = None
    calculation_method: str
    period_start: datetime
    period_end: datetime


class CarbonFootprintCreate(CarbonFootprintBase):
    pass


class CarbonFootprintResponse(CarbonFootprintBase):
    id: str
    verified: bool
    verification_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ESGScoreBase(BaseModel):
    factory_id: str
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    rating: str
    assessment_date: datetime
    criteria: Optional[Dict[str, Any]] = None
    improvements: Optional[Dict[str, Any]] = None


class ESGScoreCreate(ESGScoreBase):
    pass


class ESGScoreResponse(ESGScoreBase):
    id: str
    next_assessment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SustainabilityDashboardBase(BaseModel):
    factory_id: str
    total_waste_diverted: float = 0.0
    total_co2_saved: float = 0.0
    water_saved: float = 0.0
    energy_saved: float = 0.0
    recycling_rate: float = 0.0
    circular_economy_score: float = 0.0
    zero_waste_certified: bool = False
    green_certifications: Optional[Dict[str, Any]] = None
    period_start: datetime
    period_end: datetime


class SustainabilityDashboardCreate(SustainabilityDashboardBase):
    pass


class SustainabilityDashboardResponse(SustainabilityDashboardBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
