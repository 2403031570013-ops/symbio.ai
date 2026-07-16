from pydantic import BaseModel, ConfigDict
from typing import Optional


class MaterialBase(BaseModel):
    name: str
    chemical_composition: str
    physical_state: str
    quantity: str
    frequency: str
    certificate: str
    certificate_url: Optional[str] = None
    photo_url: Optional[str] = None
    lab_report_url: Optional[str] = None
    storage_provider: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(MaterialBase):
    pass


class MaterialOut(MaterialBase):
    id: str
    owner_id: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)
