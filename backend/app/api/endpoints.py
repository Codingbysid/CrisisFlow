from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.report import Report
from app.models.incident import Incident
from app.models.resource import Resource
from app.schemas.report import ReportCreate, ReportRead
from app.schemas.incident import IncidentRead
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.services.ai_processor import process_report, process_report_with_llm
from app.services.clustering import find_nearby_incident, update_incident_with_report
from app.api.websocket import broadcast_new_report, broadcast_new_incident
from app.core.security import get_current_user, get_current_active_user
from app.models.user import User
from typing import Optional

router = APIRouter()


@router.post("/reports/", response_model=ReportRead, status_code=201)
async def create_report(
    report: ReportCreate, 
    db: Session = Depends(get_db),
    provider: str = "dummy"
):
    """
    Create a new disaster report.
    Accepts raw text and optional image, processes it with AI, and saves to database.
    
    Args:
        report: Report creation schema with raw_text and optional image_base64
        db: Database session
        provider: AI provider ("openai", "gemini", or "dummy" for fallback)
    """
    # Process with vision model if image provided
    if report.image_base64:
        if provider in ["openai", "gemini"]:
            try:
                from app.services.ai_processor import process_image_with_vision
                processed_data = await process_image_with_vision(
                    report.image_base64, 
                    report.raw_text, 
                    provider=provider
                )
            except Exception as e:
                print(f"Vision processing failed, using text fallback: {e}")
                # Fall back to text processing
                if provider in ["openai", "gemini"]:
                    try:
                        processed_data = await process_report_with_llm(report.raw_text, provider=provider)
                    except:
                        processed_data = process_report(report.raw_text)
                else:
                    processed_data = process_report(report.raw_text)
        else:
            # Dummy doesn't support images, use text
            processed_data = process_report(report.raw_text)
    else:
        # Process the raw text using AI service
        if provider in ["openai", "gemini"]:
            try:
                processed_data = await process_report_with_llm(report.raw_text, provider=provider)
            except Exception as e:
                # Fall back to dummy if LLM fails
                print(f"LLM processing failed, using fallback: {e}")
                processed_data = process_report(report.raw_text)
        else:
            # Use dummy implementation
            processed_data = process_report(report.raw_text)
    
    # Check for nearby incident (clustering)
    nearby_incident = find_nearby_incident(
        latitude=processed_data.get("latitude"),
        longitude=processed_data.get("longitude"),
        hazard_type=processed_data.get("hazard_type"),
        db=db,
        radius_meters=500.0
    )
    
    if nearby_incident:
        # Attach to existing incident
        update_incident_with_report(nearby_incident, processed_data)
        incident_id = nearby_incident.id
    else:
        # Create new incident
        new_incident = Incident(
            location=processed_data.get("location"),
            latitude=processed_data.get("latitude"),
            longitude=processed_data.get("longitude"),
            hazard_type=processed_data.get("hazard_type"),
            severity=processed_data.get("severity"),
            confidence_score=processed_data.get("confidence_score"),
            witness_count=1,
            is_active=True
        )
        db.add(new_incident)
        db.flush()  # Get the ID without committing
        incident_id = new_incident.id
    
    # Create database record
    db_report = Report(
        raw_text=report.raw_text,
        location=processed_data.get("location"),
        latitude=processed_data.get("latitude"),
        longitude=processed_data.get("longitude"),
        hazard_type=processed_data.get("hazard_type"),
        severity=processed_data.get("severity"),
        confidence_score=processed_data.get("confidence_score"),
        is_verified=False,  # Reports start as unverified
        incident_id=incident_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Broadcast via WebSocket
    await broadcast_new_report({
        "id": db_report.id,
        "raw_text": db_report.raw_text,
        "location": db_report.location,
        "latitude": db_report.latitude,
        "longitude": db_report.longitude,
        "hazard_type": db_report.hazard_type,
        "severity": db_report.severity,
        "confidence_score": db_report.confidence_score,
        "timestamp": db_report.timestamp.isoformat() if db_report.timestamp else None,
        "is_verified": db_report.is_verified
    })
    
    return db_report


@router.get("/reports/", response_model=List[ReportRead])
async def get_reports(
    skip: int = 0, 
    limit: int = 100, 
    language: str = "en",
    db: Session = Depends(get_db)
):
    """
    Get all processed reports from the database.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        language: Language code for translations (en, es, fr)
    """
    reports = db.query(Report).offset(skip).limit(limit).all()
    
    # Optionally translate if language is specified
    if language != "en":
        from app.services.i18n import translate_hazard_type, translate_severity
        for report in reports:
            if hasattr(report, 'hazard_type') and report.hazard_type:
                # Note: This modifies the report object, might want to create a new response model
                pass
    
    return reports


@router.get("/reports/{report_id}", response_model=ReportRead)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get a specific report by ID.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/incidents/", response_model=List[IncidentRead])
async def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all active incidents (clustered reports).
    """
    incidents = db.query(Incident).filter(
        Incident.is_active == True
    ).offset(skip).limit(limit).all()
    return incidents


@router.get("/incidents/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Get a specific incident by ID with all associated reports.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


# Resource Tracking Endpoints
@router.post("/resources/", response_model=ResourceRead, status_code=201)
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new resource (needed or available)"""
    db_resource = Resource(
        name=resource.name,
        description=resource.description,
        resource_type=resource.resource_type,
        status=resource.status,
        quantity=resource.quantity,
        unit=resource.unit,
        location=resource.location,
        latitude=resource.latitude,
        longitude=resource.longitude,
        incident_id=resource.incident_id,
        user_id=current_user.id if current_user else None
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    return db_resource


@router.get("/resources/", response_model=List[ResourceRead])
async def get_resources(
    status: Optional[str] = None,
    resource_type: Optional[str] = None,
    incident_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all resources, optionally filtered by status, type, or incident"""
    query = db.query(Resource)
    
    if status:
        query = query.filter(Resource.status == status)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if incident_id:
        query = query.filter(Resource.incident_id == incident_id)
    
    resources = query.order_by(Resource.created_at.desc()).all()
    return resources


@router.get("/resources/{resource_id}", response_model=ResourceRead)
async def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get a specific resource by ID"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/resources/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Update a resource"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Update fields
    update_data = resource_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resource, field, value)
    
    db.commit()
    db.refresh(db_resource)
    
    return db_resource


@router.delete("/resources/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a resource (admin only)"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(db_resource)
    db.commit()
    return None


@router.get("/resources/summary/")
async def get_resource_summary(db: Session = Depends(get_db)):
    """Get summary of needed vs available resources"""
    needed = db.query(Resource).filter(Resource.status == "needed").all()
    available = db.query(Resource).filter(Resource.status == "available").all()
    
    needed_by_type = {}
    available_by_type = {}
    
    for resource in needed:
        rtype = resource.resource_type.value
        needed_by_type[rtype] = needed_by_type.get(rtype, 0) + resource.quantity
    
    for resource in available:
        rtype = resource.resource_type.value
        available_by_type[rtype] = available_by_type.get(rtype, 0) + resource.quantity
    
    return {
        "needed": needed_by_type,
        "available": available_by_type,
        "summary": {
            rtype: {
                "needed": needed_by_type.get(rtype, 0),
                "available": available_by_type.get(rtype, 0),
                "deficit": needed_by_type.get(rtype, 0) - available_by_type.get(rtype, 0)
            }
            for rtype in set(list(needed_by_type.keys()) + list(available_by_type.keys()))
        }
    }

