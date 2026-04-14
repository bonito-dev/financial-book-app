from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class IncomeEntry(Base):
    __tablename__ = "income_entries"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    date        = Column(Date, nullable=False)
    amount      = Column(Float, nullable=False)
    income_type = Column(String(50), nullable=False)  # Upkeep, Side, Salary, Investment
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<IncomeEntry {self.income_type} - KES {self.amount} on {self.date}>"