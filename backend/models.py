#models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True) 
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    final_itinerary = Column(JSON, nullable=True) 
    final_bill = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())