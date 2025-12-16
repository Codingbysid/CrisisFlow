from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(String, nullable=False)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    hazard_type = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Foreign key to incident
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", back_populates="reports")
    
    # Foreign key to user (who submitted the report)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User")

