from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    date             = Column(Date, nullable=False)
    account          = Column(String(50), nullable=False)  # Clothing, Wants, Investment/Savings etc.
    paid_in          = Column(Float, nullable=True)        # money coming into the bucket
    paid_out         = Column(Float, nullable=True)        # money leaving the bucket
    reason           = Column(String(200), nullable=True)
    to_be_refunded   = Column(Float, nullable=True)        # negative = overspent, needs refund
    is_tag           = Column(String(50), nullable=True)   # Investment, Savings, Debt
    created_at       = Column(DateTime, default=func.now())

    def __repr__(self):
        direction = f"IN: {self.paid_in}" if self.paid_in else f"OUT: {self.paid_out}"
        return f"<Transaction {self.account} | {direction} | {self.date}>"