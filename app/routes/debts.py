from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.debts import Debt
from app.schemas.debts import DebtCreate, DebtOut

router = APIRouter(prefix="/debts", tags=["Debts"])


# ── POST /debts — add a new debt ─────────────────────────────────
@router.post("/", response_model=DebtOut, status_code=201)
def create_debt(payload: DebtCreate, db: Session = Depends(get_db)):
    debt = Debt(
        name=payload.name,
        debt_type=payload.debt_type.value,
        original_amount=payload.original_amount,
        notes=payload.notes
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt


# ── GET /debts — fetch all debts ─────────────────────────────────
@router.get("/", response_model=list[DebtOut])
def get_debts(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Fetch all debts. By default returns only active debts.
    Pass ?active_only=false to include paid off debts.
    """
    query = db.query(Debt)
    if active_only:
        query = query.filter(Debt.is_active == True)
    return query.order_by(Debt.created_at.desc()).all()


# ── GET /debts/{id} — fetch single debt ──────────────────────────
@router.get("/{debt_id}", response_model=DebtOut)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt


# ── PATCH /debts/{id}/paid — mark debt as paid off ───────────────
@router.patch("/{debt_id}/paid", response_model=DebtOut)
def mark_debt_paid(debt_id: int, db: Session = Depends(get_db)):
    """
    Mark a debt as fully paid off.
    Uses PATCH because we're partially updating — only is_active changes.
    """
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    if not debt.is_active:
        raise HTTPException(status_code=400, detail="Debt is already marked as paid")

    debt.is_active = False
    db.commit()
    db.refresh(debt)
    return debt