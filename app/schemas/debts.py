from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class DebtTypeEnum(str, Enum):
    loan     = "Loan"
    personal = "Personal"


class DebtCreate(BaseModel):
    name:            str
    debt_type:       DebtTypeEnum
    original_amount: float
    notes:           Optional[str] = None

    @field_validator("original_amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Debt amount must be greater than zero")
        return round(value, 2)


class DebtOut(BaseModel):
    id:              int
    name:            str
    debt_type:       str
    original_amount: float
    is_active:       bool
    notes:           Optional[str]
    created_at:      datetime

    class Config:
        from_attributes = True