from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.allocations import IncomeAllocation
from app.models.transactions import Transaction
from app.schemas.balances import CategoryBalance, InvestmentSavingsBalance, BalanceSummary

router = APIRouter(prefix="/balances", tags=["Balances"])

ACCOUNTS = ["Food", "Housing", "Clothing", "Wants", "Tithe", "Fare"]


def get_category_balance(db: Session, account: str) -> CategoryBalance:
    """Calculate live balance for a single budget category."""

    # Total ever allocated to this category from income splits
    total_allocated = db.query(func.sum(IncomeAllocation.allocated_amount))\
        .filter(IncomeAllocation.category == account)\
        .scalar() or 0.0

    # Total paid into this bucket via transactions
    total_paid_in = db.query(func.sum(Transaction.paid_in))\
        .filter(Transaction.account == account)\
        .scalar() or 0.0

    # Total paid out of this bucket
    total_paid_out = db.query(func.sum(Transaction.paid_out))\
        .filter(Transaction.account == account)\
        .scalar() or 0.0

    # Total that needs to be refunded back to this bucket
    to_be_refunded = db.query(func.sum(Transaction.to_be_refunded))\
        .filter(Transaction.account == account)\
        .scalar() or 0.0

    # Account balance = what's actually in the bucket right now
    account_balance = round(total_paid_in - total_paid_out, 2)

    # Owed or surplus = how the bucket sits vs what was allocated
    # Negative = overspent (owed back), Positive = surplus
    owed_or_surplus = round(
        (total_paid_in - total_allocated) + to_be_refunded, 2
    )

    return CategoryBalance(
        account=account,
        total_allocated=round(total_allocated, 2),
        total_paid_in=round(total_paid_in, 2),
        total_paid_out=round(total_paid_out, 2),
        to_be_refunded=round(to_be_refunded, 2),
        account_balance=account_balance,
        owed_or_surplus=owed_or_surplus
    )


def get_investment_savings_balance(db: Session) -> InvestmentSavingsBalance:
    """
    Calculate the Investment/Savings balance with 50/50 sub-split.
    Uses the investment_amount and savings_amount stored per allocation.
    """

    total_allocated = db.query(func.sum(IncomeAllocation.allocated_amount))\
        .filter(IncomeAllocation.category == "Investment/Savings")\
        .scalar() or 0.0

    investment_allocated = db.query(func.sum(IncomeAllocation.investment_amount))\
        .filter(IncomeAllocation.category == "Investment/Savings")\
        .scalar() or 0.0

    savings_allocated = db.query(func.sum(IncomeAllocation.savings_amount))\
        .filter(IncomeAllocation.category == "Investment/Savings")\
        .scalar() or 0.0

    # Investment-tagged transactions (e.g. buying shares)
    investment_spent = db.query(func.sum(Transaction.paid_out))\
        .filter(
            Transaction.account == "Investment/Savings",
            Transaction.is_tag == "Investment"
        ).scalar() or 0.0

    # Include any to_be_refunded tagged as Investment
    investment_refund = db.query(func.sum(Transaction.to_be_refunded))\
        .filter(
            Transaction.account == "Investment/Savings",
            Transaction.is_tag == "Investment"
        ).scalar() or 0.0

    # Savings-tagged transactions
    savings_spent = db.query(func.sum(Transaction.paid_out))\
        .filter(
            Transaction.account == "Investment/Savings",
            Transaction.is_tag == "Savings"
        ).scalar() or 0.0

    savings_refund = db.query(func.sum(Transaction.to_be_refunded))\
        .filter(
            Transaction.account == "Investment/Savings",
            Transaction.is_tag == "Savings"
        ).scalar() or 0.0

    investment_balance = round(
        investment_allocated - investment_spent + (investment_refund or 0.0), 2
    )
    savings_balance = round(
        savings_allocated - savings_spent + (savings_refund or 0.0), 2
    )

    return InvestmentSavingsBalance(
        total_allocated=round(total_allocated, 2),
        investment_allocated=round(investment_allocated, 2),
        savings_allocated=round(savings_allocated, 2),
        investment_spent=round(investment_spent, 2),
        savings_spent=round(savings_spent, 2),
        investment_balance=investment_balance,
        savings_balance=savings_balance
    )


# ── GET /balances — full balance summary ─────────────────────────
@router.get("/", response_model=BalanceSummary)
def get_balances(db: Session = Depends(get_db)):
    """
    Live balance summary across all budget categories.
    Calculated fresh from income allocations and transactions.
    """
    categories = [get_category_balance(db, account) for account in ACCOUNTS]
    investment_savings = get_investment_savings_balance(db)

    total_owed_surplus = round(
        sum(c.owed_or_surplus for c in categories) +
        investment_savings.investment_balance +
        investment_savings.savings_balance, 2
    )

    total_account_balance = round(
        sum(c.account_balance for c in categories) +
        investment_savings.total_allocated, 2
    )

    return BalanceSummary(
        categories=categories,
        investment_savings=investment_savings,
        total_owed_surplus=total_owed_surplus,
        total_account_balance=total_account_balance
    )


# ── GET /balances/{account} — single category balance ────────────
@router.get("/{account}", response_model=CategoryBalance)
def get_category_balance_by_name(account: str, db: Session = Depends(get_db)):
    """
    Fetch live balance for a single budget category.
    e.g. /balances/Wants  or  /balances/Fare
    """
    valid_accounts = ACCOUNTS + ["Investment/Savings"]
    if account not in valid_accounts:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Account '{account}' not found. Valid: {valid_accounts}"
        )
    return get_category_balance(db, account)