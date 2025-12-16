from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReportCreate(BaseModel):
    """Schema for creating a report (receiving raw text)"""
    raw_text: str = Field(..., description="Raw text report from user")


class ReportRead(BaseModel):
    """Schema for reading a report (returning processed fields)"""
    id: int
    raw_text: str
    location: Optional[str] = None
    hazard_type: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: datetime
    is_verified: bool

    class Config:
        from_attributes = True

