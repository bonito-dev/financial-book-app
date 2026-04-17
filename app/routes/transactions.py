from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transactions import Transaction
from app.schemas.transactions import TransactionCreate, TransactionOut
from typing import Optional
from datetime import date

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# ── POST /transactions — log a new transaction ───────────────────
@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Log a transaction — money moving in or out of a budget bucket.
    """
    transaction = Transaction(
        date=payload.date,
        account=payload.account.value,
        paid_in=payload.paid_in,
        paid_out=payload.paid_out,
        reason=payload.reason,
        to_be_refunded=payload.to_be_refunded,
        is_tag=payload.is_tag.value if payload.is_tag else None
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


# ── GET /transactions — fetch all transactions ───────────────────
@router.get("/", response_model=list[TransactionOut])
def get_transactions(
    account: Optional[str] = None,
    month: Optional[str] = None,
    is_tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch all transactions.
    Filter by account, month (YYYY-MM), or investment/savings tag.
    """
    query = db.query(Transaction)

    if account:
        query = query.filter(Transaction.account == account)

    if is_tag:
        query = query.filter(Transaction.is_tag == is_tag)

    if month:
        try:
            year, mon = month.split("-")
            query = query.filter(
                Transaction.date >= date(int(year), int(mon), 1),
                Transaction.date <= date(int(year), int(mon), 28)
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM e.g. 2026-01"
            )

    return query.order_by(Transaction.date.desc()).all()


# ── GET /transactions/{id} — fetch single transaction ────────────
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


# ── DELETE /transactions/{id} — remove a transaction ─────────────
@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Delete a transaction by ID.
    Use carefully — this affects bucket balances.
    """
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()