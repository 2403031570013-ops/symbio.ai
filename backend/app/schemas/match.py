from pydantic import BaseModel, ConfigDict
from typing import Optional


class MatchBase(BaseModel):
    material_id: str
    partner_name: str
    symbio_score: int
    distance_km: float
    carbon_savings: str
    summary: Optional[str] = None


class MatchCreate(MatchBase):
    pass


class MatchOut(MatchBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
