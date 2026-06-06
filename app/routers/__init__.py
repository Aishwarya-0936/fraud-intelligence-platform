from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionResponse
from typing import List
import uuid

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        merchant=transaction.merchant,
        location=transaction.location,
        device_id=transaction.device_id,
        transaction_type=transaction.transaction_type,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(
        Transaction.timestamp.desc()
    ).offset(skip).limit(limit).all()
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction