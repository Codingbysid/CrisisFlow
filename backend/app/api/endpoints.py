from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportRead
from app.services.ai_processor import process_report, process_report_with_llm

router = APIRouter()


@router.post("/reports/", response_model=ReportRead, status_code=201)
async def create_report(
    report: ReportCreate, 
    db: Session = Depends(get_db),
    provider: str = "dummy"
):
    """
    Create a new disaster report.
    Accepts raw text, processes it with AI, and saves to database.
    
    Args:
        report: Report creation schema with raw_text
        db: Database session
        provider: AI provider ("openai", "gemini", or "dummy" for fallback)
    """
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
    
    # Create database record
    db_report = Report(
        raw_text=report.raw_text,
        location=processed_data.get("location"),
        hazard_type=processed_data.get("hazard_type"),
        severity=processed_data.get("severity"),
        confidence_score=processed_data.get("confidence_score"),
        is_verified=False  # Reports start as unverified
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

