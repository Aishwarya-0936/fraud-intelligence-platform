from pydantic import BaseModel, UUID4
from decimal import Decimal
from datetime import datetime
from typing import Optional
from typing import List

class TransactionCreate(BaseModel):
    user_id: str
    amount: Decimal
    merchant: Optional[str] = None
    merchant_category: Optional[str] = None
    location: Optional[str] = None
    device_id: Optional[str] = None
    destination_account: Optional[str] = None
    transaction_type: str
    idempotency_key: Optional[str] = None

class TransactionResponse(BaseModel):
    id: UUID4
    user_id: str
    amount: Decimal
    merchant: Optional[str] = None
    merchant_category: Optional[str] = None
    location: Optional[str] = None
    device_id: Optional[str] = None
    destination_account: Optional[str] = None
    transaction_type: str
    timestamp: datetime
    status: str
    risk_score: Decimal
    risk_level: str
    signals: Optional[str] = None
    summary: Optional[str] = None
    review_decision: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionReviewRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    reviewer_notes: Optional[str] = None

class LoginEventCreate(BaseModel):
    user_id: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    success: str
    
class ReviewRequest(BaseModel):
    decision: str
    reviewer_notes: Optional[str] = None

class LoginEventResponse(BaseModel):
    id: UUID4
    user_id: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    success: str
    timestamp: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[TransactionResponse]