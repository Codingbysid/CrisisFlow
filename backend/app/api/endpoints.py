from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.report import Report
from app.models.incident import Incident
from app.schemas.report import ReportCreate, ReportRead
from app.schemas.incident import IncidentRead
from app.services.ai_processor import process_report, process_report_with_llm
from app.services.clustering import find_nearby_incident, update_incident_with_report

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
    
    return db_report


@router.get("/reports/", response_model=List[ReportRead])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all processed reports from the database.
    """
    reports = db.query(Report).offset(skip).limit(limit).all()
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

