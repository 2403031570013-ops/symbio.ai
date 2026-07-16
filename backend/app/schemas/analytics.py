from pydantic import BaseModel, ConfigDict


class AnalyticsOut(BaseModel):
    revenue_generated: float
    co2_avoided: float
    landfill_diversion: float
    active_matches: float

    model_config = ConfigDict(from_attributes=True)
