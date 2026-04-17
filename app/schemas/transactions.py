from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional
from enum import Enum


class AccountEnum(str, Enum):
    food                = "Food"
    housing             = "Housing"
    clothing            = "Clothing"
    wants               = "Wants"
    investment_savings  = "Investment/Savings"
    tithe               = "Tithe"
    fare                = "Fare"


class ISTagEnum(str, Enum):
    investment  = "Investment"
    savings     = "Savings"
    debt        = "Debt"


class TransactionCreate(BaseModel):
    date:            date
    account:         AccountEnum
    paid_in:         Optional[float] = None
    paid_out:        Optional[float] = None
    reason:          Optional[str] = None
    to_be_refunded:  Optional[float] = None
    is_tag:          Optional[ISTagEnum] = None

    @model_validator(mode="after")
    def must_have_one_direction(self):
        if self.paid_in is None and self.paid_out is None:
            raise ValueError("Transaction must have either paid_in or paid_out")
        if self.paid_in is not None and self.paid_out is not None:
            raise ValueError("Transaction cannot have both paid_in and paid_out")
        return self


class TransactionOut(BaseModel):
    id:              int
    date:            date
    account:         str
    paid_in:         Optional[float]
    paid_out:        Optional[float]
    reason:          Optional[str]
    to_be_refunded:  Optional[float]
    is_tag:          Optional[str]

    class Config:
        from_attributes = True