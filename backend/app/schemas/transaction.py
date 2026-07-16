from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    material_id: str
    partner_name: str
    amount: float
    status: str = "Pending"


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
