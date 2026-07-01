from sqlalchemy import Column, String, Numeric, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    merchant = Column(String, nullable=True)
    merchant_category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    destination_account = Column(String, nullable=True)
    transaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")
    risk_score = Column(Numeric(5, 2), default=0)
    risk_level = Column(String, default="LOW")
    signals = Column(String, nullable=True)
    summary = Column(String, nullable=True)

class UserLoginEvent(Base):
    __tablename__ = "user_login_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    device_id = Column(String, nullable=True)
    location = Column(String, nullable=True)
    success = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())