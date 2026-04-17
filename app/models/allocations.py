from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class IncomeAllocation(Base):
    __tablename__ = "income_allocations"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    income_entry_id   = Column(Integer, ForeignKey("income_entries.id"), nullable=False)
    budget_rule_id    = Column(Integer, ForeignKey("budget_rules.id"), nullable=False)
    category          = Column(String(50), nullable=False)
    allocated_amount  = Column(Float, nullable=False)

    # Investment/Savings sub-split
    investment_amount = Column(Float, nullable=True)  # allocated_amount / 2
    savings_amount    = Column(Float, nullable=True)  # allocated_amount / 2

    created_at        = Column(DateTime, default=func.now())

    income_entry = relationship("IncomeEntry", backref="allocations")
    budget_rule  = relationship("BudgetRule", backref="allocations")

    def __repr__(self):
        return f"<Allocation {self.category}: KES {self.allocated_amount}>"