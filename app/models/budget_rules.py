from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    income_type   = Column(String(50), nullable=False)   # Upkeep, Side, Salary, Investment
    category      = Column(String(50), nullable=False)   # Food, Clothing, Investment, etc.
    percentage    = Column(Float, nullable=True)         # e.g. 0.30 for 30%
    is_fixed      = Column(Boolean, default=False)       # True = fixed amount, False = percentage
    fixed_amount  = Column(Float, nullable=True)         # only used when is_fixed = True
    condition     = Column(String(50), nullable=True)    # e.g. only apply when income_type = 'Salary'
    valid_from    = Column(Date, nullable=False)         # when this rule became active
    valid_to      = Column(Date, nullable=True)          # NULL = currently active rule
    is_current    = Column(Boolean, default=True)        # quick filter for active rules
    created_at    = Column(DateTime, default=func.now())

    def __repr__(self):
        rule = f"{self.percentage*100}%" if not self.is_fixed else f"KES {self.fixed_amount}"
        return f"<BudgetRule {self.income_type} → {self.category}: {rule}>"