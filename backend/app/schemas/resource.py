from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.resource import ResourceType, ResourceStatus


class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    resource_type: ResourceType
    status: ResourceStatus = ResourceStatus.NEEDED
    quantity: float
    unit: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_id: Optional[int] = None


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    status: Optional[ResourceStatus] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_id: Optional[int] = None


class ResourceRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    resource_type: ResourceType
    status: ResourceStatus
    quantity: float
    unit: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

