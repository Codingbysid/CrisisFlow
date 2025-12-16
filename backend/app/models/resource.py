from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ResourceType(str, enum.Enum):
    WATER = "water"
    FOOD = "food"
    MEDICAL = "medical"
    SHELTER = "shelter"
    TRANSPORT = "transport"
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    OTHER = "other"


class ResourceStatus(str, enum.Enum):
    NEEDED = "needed"
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    status = Column(Enum(ResourceStatus), default=ResourceStatus.NEEDED, nullable=False)
    quantity = Column(Float, nullable=False)  # Can be decimal for partial units
    unit = Column(String, nullable=False)  # e.g., "liters", "people", "units"
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Link to incident if resource is for specific incident
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", backref="resources")
    
    # Link to user who created/updated resource
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

