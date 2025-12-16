from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReportCreate(BaseModel):
    """Schema for creating a report (receiving raw text and optional image)"""
    raw_text: str = Field(..., description="Raw text report from user")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image (optional)")


class ReportRead(BaseModel):
    """Schema for reading a report (returning processed fields)"""
    id: int
    raw_text: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hazard_type: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: datetime
    is_verified: bool

    class Config:
        from_attributes = True

