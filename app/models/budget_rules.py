from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    income_category  = Column(String(50), nullable=False)  # The 7 categories
    category         = Column(String(50), nullable=False)  # Food, Housing, Clothing, etc.
    parent_category  = Column(String(50), nullable=True)   # e.g. 'Needs' groups Food+Housing+Clothing
    percentage       = Column(Float, nullable=True)        # e.g. 0.25 for 25%
    is_fixed         = Column(Boolean, default=False)      # True = fixed amount
    fixed_amount     = Column(Float, nullable=True)        # only when is_fixed = True
    deduct_first     = Column(Boolean, default=False)      # True = deduct before other calculations (Fare)
    valid_from       = Column(Date, nullable=False)
    valid_to         = Column(Date, nullable=True)         # NULL = currently active
    is_current       = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=func.now())

    def __repr__(self):
        rule = f"{self.percentage*100}%" if not self.is_fixed else f"KES {self.fixed_amount}"
        return f"<BudgetRule {self.income_category} → {self.category}: {rule}>"