from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.income import IncomeEntry
from app.schemas.income import IncomeEntryCreate, IncomeEntryOut
from app.core.allocation_engine import process_income_allocation
from typing import Optional
from datetime import date

router = APIRouter(prefix="/income", tags=["Income"])


# ── POST /income — log a new income entry ────────────────────────
@router.post("/", response_model=IncomeEntryOut, status_code=201)
def create_income_entry(
    payload: IncomeEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Log a new income entry and automatically allocate it
    across budget categories based on active rules.
    """
    # Step 1: Save the income entry
    entry = IncomeEntry(
        date=payload.date,
        amount=payload.amount,
        income_category=payload.income_category.value,
        income_subtype=payload.income_subtype,
        notes=payload.notes
    )
    db.add(entry)
    db.flush()  # writes to DB session but doesn't commit yet — we need the ID

    # Step 2: Run the allocation engine
    try:
        allocations = process_income_allocation(
            db=db,
            income_entry_id=entry.id,
            income_category=entry.income_category,
            gross_amount=entry.amount,
            entry_date=entry.date
        )
    except ValueError as e:
        db.rollback()  # undo the income entry if allocation fails
        raise HTTPException(status_code=400, detail=str(e))

    # Step 3: Commit the income entry (allocations already committed inside engine)
    db.commit()
    db.refresh(entry)

    # Build response manually since allocations come from engine output
    return IncomeEntryOut(
        id=entry.id,
        date=entry.date,
        amount=entry.amount,
        income_category=entry.income_category,
        income_subtype=entry.income_subtype,
        notes=entry.notes,
        allocations=allocations
    )


# ── GET /income — fetch all income entries ────────────────────────
@router.get("/", response_model=list[IncomeEntryOut])
def get_income_entries(
    month: Optional[str] = None,   # e.g. "2026-01"
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch all income entries.
    Optionally filter by month (YYYY-MM) or income category.
    """
    query = db.query(IncomeEntry)

    if month:
        try:
            year, mon = month.split("-")
            query = query.filter(
                IncomeEntry.date >= date(int(year), int(mon), 1),
                IncomeEntry.date <= date(int(year), int(mon), 28)  # safe lower bound
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM e.g. 2026-01"
            )

    if category:
        query = query.filter(IncomeEntry.income_category == category)

    entries = query.order_by(IncomeEntry.date.desc()).all()

    # Return entries without allocations for list view (cleaner response)
    return [
        IncomeEntryOut(
            id=e.id,
            date=e.date,
            amount=e.amount,
            income_category=e.income_category,
            income_subtype=e.income_subtype,
            notes=e.notes,
            allocations=[]
        )
        for e in entries
    ]


# ── GET /income/{id} — fetch single income entry with allocations ─
@router.get("/{entry_id}", response_model=IncomeEntryOut)
def get_income_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single income entry by ID, including its full allocation breakdown.
    """
    entry = db.query(IncomeEntry).filter(IncomeEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Income entry not found")

    # Fetch allocations for this entry
    from app.models.allocations import IncomeAllocation
    raw_allocations = db.query(IncomeAllocation)\
        .filter(IncomeAllocation.income_entry_id == entry_id).all()

    allocations = [
        {
            "category": a.category,
            "allocated_amount": a.allocated_amount,
            "type": "deduction" if a.budget_rule_id else "percentage",
            "rule_id": a.budget_rule_id
        }
        for a in raw_allocations
    ]

    return IncomeEntryOut(
        id=entry.id,
        date=entry.date,
        amount=entry.amount,
        income_category=entry.income_category,
        income_subtype=entry.income_subtype,
        notes=entry.notes,
        allocations=allocations
    )