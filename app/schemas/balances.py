from pydantic import BaseModel
from typing import Optional


class CategoryBalance(BaseModel):
    account:          str
    total_allocated:  float
    total_paid_in:    float
    total_paid_out:   float
    to_be_refunded:   float
    account_balance:  float
    owed_or_surplus:  float


class InvestmentSavingsBalance(BaseModel):
    total_allocated:   float
    investment_allocated: float
    savings_allocated: float
    investment_spent:  float
    savings_spent:     float
    investment_balance: float
    savings_balance:   float


class BalanceSummary(BaseModel):
    categories:          list[CategoryBalance]
    investment_savings:  InvestmentSavingsBalance
    total_owed_surplus:  float
    total_account_balance: float