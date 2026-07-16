from typing import Optional
from pydantic import BaseModel, ConfigDict


class FactoryBase(BaseModel):
    name: str
    industry: str
    location: str


class FactoryCreate(FactoryBase):
    pass


class FactoryUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    verified: Optional[bool] = None


class FactoryOut(FactoryBase):
    id: str
    verified: bool
    owner_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
