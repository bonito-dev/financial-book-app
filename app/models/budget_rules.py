from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    income_category  = Column(String(50), nullable=False)
    category         = Column(String(50), nullable=False)
    parent_category  = Column(String(50), nullable=True)
    percentage       = Column(Float, nullable=True)
    is_fixed         = Column(Boolean, default=False)
    fixed_amount     = Column(Float, nullable=True)
    deduct_first     = Column(Boolean, default=False)
    deduction_order  = Column(Integer, nullable=True)  # 1 = first, 2 = second, etc.
    is_topup         = Column(Boolean, default=False)  # top up to target vs blind add
    topup_target     = Column(Float, nullable=True)    # e.g. 5000.0
    topup_day        = Column(Integer, nullable=True)  # day of month to trigger (e.g. 1)
    valid_from       = Column(Date, nullable=False)
    valid_to         = Column(Date, nullable=True)
    is_current       = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=func.now())

    def __repr__(self):
        if self.is_topup:
            rule = f"Top-up to KES {self.topup_target} on day {self.topup_day}"
        elif self.is_fixed:
            rule = f"Fixed KES {self.fixed_amount}"
        else:
            rule = f"{self.percentage * 100}%"
        return f"<BudgetRule {self.income_category} → {self.category}: {rule}>"