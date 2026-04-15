from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional
from enum import Enum


# ── Enums — locked list of valid values ──────────────────────────
class IncomeCategoryEnum(str, Enum):
    earned      = "Earned Income"
    passive     = "Passive Income"
    business    = "Business Income"
    investment  = "Investment Income"
    transfer    = "Transfer Income"
    residual    = "Residual Income"
    other       = "Other"


# ── Request schema (what comes IN) ───────────────────────────────
class IncomeEntryCreate(BaseModel):
    date:             date
    amount:           float
    income_category:  IncomeCategoryEnum
    income_subtype:   Optional[str] = None
    notes:            Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(value, 2)


# ── Allocation schema (used inside responses) ────────────────────
class AllocationOut(BaseModel):
    category:         str
    allocated_amount: float
    type:             str  # 'deduction' or 'percentage'
    rule_id:          int

    class Config:
        from_attributes = True


# ── Response schema (what goes OUT) ──────────────────────────────
class IncomeEntryOut(BaseModel):
    id:               int
    date:             date
    amount:           float
    income_category:  str
    income_subtype:   Optional[str]
    notes:            Optional[str]
    allocations:      list[AllocationOut] = []

    class Config:
        from_attributes = True