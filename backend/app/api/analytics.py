from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models.report import Report
from app.models.incident import Incident
from app.models.resource import Resource
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter()


@router.get("/reports/historical/")
async def get_historical_reports(
    days: int = 7,
    hazard_type: str = None,
    db: Session = Depends(get_db)
):
    """
    Get historical report data for analysis
    
    Args:
        days: Number of days to look back
        hazard_type: Filter by hazard type (optional)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(Report).filter(Report.timestamp >= cutoff_date)
    
    if hazard_type:
        query = query.filter(Report.hazard_type == hazard_type)
    
    reports = query.all()
    
    # Group by date
    by_date = {}
    by_severity = {"Low": 0, "Medium": 0, "High": 0}
    by_hazard = {}
    
    for report in reports:
        # By date
        date_key = report.timestamp.date().isoformat() if report.timestamp else "unknown"
        by_date[date_key] = by_date.get(date_key, 0) + 1
        
        # By severity
        if report.severity:
            by_severity[report.severity] = by_severity.get(report.severity, 0) + 1
        
        # By hazard type
        hazard = report.hazard_type or "Unknown"
        by_hazard[hazard] = by_hazard.get(hazard, 0) + 1
    
    return {
        "period_days": days,
        "total_reports": len(reports),
        "by_date": by_date,
        "by_severity": by_severity,
        "by_hazard_type": by_hazard,
        "average_confidence": sum(r.confidence_score or 0 for r in reports) / len(reports) if reports else 0
    }


@router.get("/incidents/trends/")
async def get_incident_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get incident trends over time"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    incidents = db.query(Incident).filter(
        Incident.created_at >= cutoff_date
    ).all()
    
    # Group by date
    by_date = {}
    active_count = 0
    total_witnesses = 0
    
    for incident in incidents:
        date_key = incident.created_at.date().isoformat() if incident.created_at else "unknown"
        by_date[date_key] = by_date.get(date_key, 0) + 1
        
        if incident.is_active:
            active_count += 1
            total_witnesses += incident.witness_count
    
    return {
        "period_days": days,
        "total_incidents": len(incidents),
        "active_incidents": active_count,
        "total_witnesses": total_witnesses,
        "by_date": by_date,
        "average_witnesses_per_incident": total_witnesses / active_count if active_count > 0 else 0
    }


@router.get("/resources/trends/")
async def get_resource_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get resource trends"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    resources = db.query(Resource).filter(
        Resource.created_at >= cutoff_date
    ).all()
    
    needed_by_type = {}
    available_by_type = {}
    
    for resource in resources:
        rtype = resource.resource_type.value
        if resource.status.value == "needed":
            needed_by_type[rtype] = needed_by_type.get(rtype, 0) + resource.quantity
        elif resource.status.value == "available":
            available_by_type[rtype] = available_by_type.get(rtype, 0) + resource.quantity
    
    return {
        "period_days": days,
        "needed_by_type": needed_by_type,
        "available_by_type": available_by_type,
        "deficits": {
            rtype: needed_by_type.get(rtype, 0) - available_by_type.get(rtype, 0)
            for rtype in set(list(needed_by_type.keys()) + list(available_by_type.keys()))
        }
    }


@router.get("/dashboard/stats/")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics"""
    total_reports = db.query(Report).count()
    active_incidents = db.query(Incident).filter(Incident.is_active == True).count()
    total_resources_needed = db.query(Resource).filter(Resource.status == "needed").count()
    total_resources_available = db.query(Resource).filter(Resource.status == "available").count()
    
    # Recent activity (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_reports = db.query(Report).filter(Report.timestamp >= last_24h).count()
    recent_incidents = db.query(Incident).filter(Incident.created_at >= last_24h).count()
    
    return {
        "total_reports": total_reports,
        "active_incidents": active_incidents,
        "resources_needed": total_resources_needed,
        "resources_available": total_resources_available,
        "recent_activity_24h": {
            "reports": recent_reports,
            "incidents": recent_incidents
        }
    }

