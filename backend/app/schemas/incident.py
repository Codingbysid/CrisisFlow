from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.report import ReportRead


class IncidentRead(BaseModel):
    """Schema for reading an incident"""
    id: int
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hazard_type: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: Optional[float] = None
    witness_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    reports: List[ReportRead] = []

    class Config:
        from_attributes = True

