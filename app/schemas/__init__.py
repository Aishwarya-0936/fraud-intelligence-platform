from pydantic import BaseModel, UUID4
from decimal import Decimal
from datetime import datetime
from typing import Optional

class TransactionCreate(BaseModel):
    user_id: str
    amount: Decimal
    merchant: Optional[str] = None
    location: Optional[str] = None
    device_id: Optional[str] = None
    transaction_type: str

class TransactionResponse(BaseModel):
    id: UUID4
    user_id: str
    amount: Decimal
    merchant: Optional[str] = None
    location: Optional[str] = None
    device_id: Optional[str] = None
    transaction_type: str
    timestamp: datetime
    status: str
    risk_score: Decimal
    risk_level: str
    signals: Optional[str] = None

    class Config:
        from_attributes = True