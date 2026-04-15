from sqlalchemy.orm import Session
from app.models.budget_rules import BudgetRule
from app.models.allocations import IncomeAllocation
from app.models.transactions import Transaction
from datetime import date
from typing import Optional


def get_fare_bucket_balance(db: Session) -> float:
    """
    Calculate the current balance of the Fare bucket.
    Balance = total paid in - total paid out across all Fare transactions.
    """
    from sqlalchemy import func

    paid_in = db.query(func.sum(Transaction.paid_in))\
        .filter(Transaction.account == "Fare")\
        .scalar() or 0.0

    paid_out = db.query(func.sum(Transaction.paid_out))\
        .filter(Transaction.account == "Fare")\
        .scalar() or 0.0

    return paid_in - paid_out


def calculate_fare_topup(db: Session, target: float) -> float:
    """
    Calculate how much needs to be added to Fare bucket
    to reach the target. Returns 0 if already at or above target.
    """
    current_balance = get_fare_bucket_balance(db)
    shortfall = target - current_balance
    return max(0.0, shortfall)  # never return a negative top-up


def process_income_allocation(
    db: Session,
    income_entry_id: int,
    income_category: str,
    gross_amount: float,
    entry_date: Optional[date] = None
) -> list[dict]:
    """
    Core allocation engine.
    Takes an income entry and splits it into budget categories
    based on the active rules for that income category.

    Returns a list of allocation dicts for inspection/response.
    """

    if entry_date is None:
        entry_date = date.today()

    # ── Step 1: Fetch all active rules for this income category ──
    rules = db.query(BudgetRule).filter(
        BudgetRule.income_category == income_category,
        BudgetRule.is_current == True
    ).order_by(BudgetRule.deduction_order.nulls_last()).all()
    # nulls_last() → deduct_first rules (with order 1, 2) sort before
    # percentage rules (whose deduction_order is NULL)

    if not rules:
        raise ValueError(f"No active budget rules found for: {income_category}")

    # ── Step 2: Separate deductions from percentage rules ─────────
    deduction_rules = [r for r in rules if r.deduct_first]
    percentage_rules = [r for r in rules if not r.deduct_first]

    allocations = []
    total_deducted = 0.0
    remaining = gross_amount

    # ── Step 3: Process deductions in order ───────────────────────
    for rule in sorted(deduction_rules, key=lambda r: r.deduction_order or 0):

        if rule.is_topup:
            # Top-up logic: only allocate what's needed to reach target
            # Only trigger on the 1st of the month
            if entry_date.day == rule.topup_day:
                allocated = calculate_fare_topup(db, rule.topup_target)
            else:
                allocated = 0.0  # not the right day — skip

        elif rule.is_fixed:
            allocated = rule.fixed_amount or 0.0

        else:
            # Percentage-based deduction (e.g. Tithe = 10% of gross)
            allocated = round(gross_amount * (rule.percentage or 0.0), 2)

        total_deducted += allocated
        remaining = round(gross_amount - total_deducted, 2)

        # Save this allocation
        allocation = IncomeAllocation(
            income_entry_id=income_entry_id,
            budget_rule_id=rule.id,
            category=rule.category,
            allocated_amount=allocated
        )
        db.add(allocation)
        allocations.append({
            "category": rule.category,
            "allocated_amount": allocated,
            "type": "deduction",
            "rule_id": rule.id
        })

    # ── Step 4: Apply percentage rules to remaining amount ────────
    for rule in percentage_rules:
        allocated = round(remaining * (rule.percentage or 0.0), 2)

        allocation = IncomeAllocation(
            income_entry_id=income_entry_id,
            budget_rule_id=rule.id,
            category=rule.category,
            allocated_amount=allocated
        )
        db.add(allocation)
        allocations.append({
            "category": rule.category,
            "allocated_amount": allocated,
            "type": "percentage",
            "rule_id": rule.id
        })

    # ── Step 5: Commit all allocations together ───────────────────
    db.commit()

    return allocations