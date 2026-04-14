from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class IncomeEntry(Base):
    __tablename__ = "income_entries"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    date             = Column(Date, nullable=False)
    amount           = Column(Float, nullable=False)
    income_category  = Column(String(50), nullable=False)  # The 7 categories
    income_subtype   = Column(String(50), nullable=True)   # e.g. 'Salary', 'Upkeep', 'Freelancing'
    notes            = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=func.now())

    def __repr__(self):
        sub = f" ({self.income_subtype})" if self.income_subtype else ""
        return f"<IncomeEntry {self.income_category}{sub} - KES {self.amount} on {self.date}>"