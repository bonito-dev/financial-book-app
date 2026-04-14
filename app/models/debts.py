from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Debt(Base):
    __tablename__ = "debts"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(100), nullable=False)   # e.g. 'ZK Pesa', 'Hustler Fund'
    debt_type      = Column(String(50), nullable=False)    # 'Loan' or 'Personal'
    original_amount = Column(Float, nullable=False)
    is_active      = Column(Boolean, default=True)         # False = fully paid off
    notes          = Column(Text, nullable=True)
    created_at     = Column(DateTime, default=func.now())

    def __repr__(self):
        status = "Active" if self.is_active else "Paid Off"
        return f"<Debt {self.name}: KES {self.original_amount} | {status}>"