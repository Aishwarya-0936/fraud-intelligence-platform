from fastapi import APIRouter, Depends, HTTPException, Query
from app.risk_engine import get_user_profile, update_user_profile, update_failed_logins, reset_failed_logins
from app.agents.graph import run_fraud_analysis
from app.rate_limiter import is_rate_limited
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db import get_db
from app.models import Transaction, UserLoginEvent
from app.schemas import (
    TransactionCreate, TransactionResponse, TransactionListResponse,
    TransactionReviewRequest,
    LoginEventCreate, LoginEventResponse
)
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/transactions", tags=["transactions"])
login_router = APIRouter(prefix="/logins", tags=["logins"])


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    if await is_rate_limited(transaction.user_id):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    # Idempotency check — if this exact request was already processed, return the original result
    # instead of scoring it again (protects against network retries, double-submits, etc.)
    if transaction.idempotency_key:
        existing = await db.execute(
            select(Transaction).where(Transaction.idempotency_key == transaction.idempotency_key)
        )
        existing_transaction = existing.scalar_one_or_none()
        if existing_transaction:
            return existing_transaction

    db_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        merchant=transaction.merchant,
        merchant_category=transaction.merchant_category,
        location=transaction.location,
        device_id=transaction.device_id,
        destination_account=transaction.destination_account,
        transaction_type=transaction.transaction_type,
        idempotency_key=transaction.idempotency_key,
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    transaction_data = {
        "user_id": transaction.user_id,
        "amount": str(transaction.amount),
        "merchant": transaction.merchant,
        "device_id": transaction.device_id,
        "location": transaction.location,
        "destination_account": transaction.destination_account,
        "merchant_category": transaction.merchant_category,
        "transaction_type": transaction.transaction_type,
        "timestamp": db_transaction.timestamp.isoformat()
    }

    profile = await get_user_profile(transaction.user_id)
    result = await run_fraud_analysis(transaction_data, profile)
    await update_user_profile(transaction.user_id, transaction_data, profile)

    db_transaction.risk_score = result["total_score"]
    db_transaction.risk_level = result["risk_level"]
    db_transaction.signals = ", ".join(result["all_signals"]) if result["all_signals"] else None
    db_transaction.summary = result["summary"]
    if result["risk_level"] == "CRITICAL":
        db_transaction.status = "pending_review"
    elif result["risk_level"] == "HIGH":
        db_transaction.status = "flagged"
    else:
        db_transaction.status = "cleared"

    await db.commit()
    await db.refresh(db_transaction)

    return db_transaction


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: LOW, MEDIUM, HIGH, CRITICAL"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Transaction)
    count_query = select(func.count()).select_from(Transaction)

    if risk_level:
        query = query.where(Transaction.risk_level == risk_level.upper())
        count_query = count_query.where(Transaction.risk_level == risk_level.upper())

    if user_id:
        query = query.where(Transaction.user_id == user_id)
        count_query = count_query.where(Transaction.user_id == user_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Transaction.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return TransactionListResponse(total=total, skip=skip, limit=limit, items=items)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/{transaction_id}/review", response_model=TransactionResponse)
async def review_transaction(
    transaction_id: uuid.UUID,
    review: TransactionReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.status != "pending_review":
        raise HTTPException(status_code=400, detail="This transaction is not awaiting review")

    if review.decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    transaction.review_decision = review.decision
    transaction.reviewed_at = datetime.utcnow()
    transaction.status = "cleared" if review.decision == "approved" else "blocked"

    await db.commit()
    await db.refresh(transaction)
    return transaction


@login_router.post("/", response_model=LoginEventResponse)
async def record_login(login: LoginEventCreate, db: AsyncSession = Depends(get_db)):
    db_login = UserLoginEvent(
        user_id=login.user_id,
        device_id=login.device_id,
        location=login.location,
        success=login.success
    )
    db.add(db_login)
    await db.commit()
    await db.refresh(db_login)

    if login.success == "false":
        await update_failed_logins(login.user_id)
    else:
        await reset_failed_logins(login.user_id)

    return db_login