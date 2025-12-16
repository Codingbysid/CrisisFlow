from geopy.distance import geodesic
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.report import Report


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in meters.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in meters
    """
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')
    
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def find_nearby_incident(
    latitude: Optional[float],
    longitude: Optional[float],
    hazard_type: Optional[str],
    db: Session,
    radius_meters: float = 500.0
) -> Optional[Incident]:
    """
    Find an existing active incident within the specified radius.
    
    Args:
        latitude: Report latitude
        longitude: Report longitude
        hazard_type: Type of hazard
        db: Database session
        radius_meters: Search radius in meters (default 500m)
        
    Returns:
        Incident if found, None otherwise
    """
    if latitude is None or longitude is None:
        return None
    
    # Get all active incidents with the same hazard type
    active_incidents = db.query(Incident).filter(
        Incident.is_active == True,
        Incident.hazard_type == hazard_type,
        Incident.latitude.isnot(None),
        Incident.longitude.isnot(None)
    ).all()
    
    for incident in active_incidents:
        distance = calculate_distance(
            latitude, longitude,
            incident.latitude, incident.longitude
        )
        
        if distance <= radius_meters:
            return incident
    
    return None


def update_incident_with_report(incident: Incident, report_data: dict) -> None:
    """
    Update an incident's metadata based on a new report.
    Increases witness count, updates confidence, and potentially severity.
    
    Args:
        incident: The incident to update
        report_data: Dictionary with report data (severity, confidence_score)
    """
    # Increase witness count
    incident.witness_count += 1
    
    # Update confidence score (average or max, using max for now)
    new_confidence = report_data.get("confidence_score", 0.0)
    if incident.confidence_score is None:
        incident.confidence_score = new_confidence
    else:
        # Use weighted average (favor higher confidence)
        incident.confidence_score = max(incident.confidence_score, new_confidence)
    
    # Update severity if new report indicates higher severity
    severity_order = {"Low": 1, "Medium": 2, "High": 3}
    new_severity = report_data.get("severity", "Low")
    current_severity = incident.severity or "Low"
    
    if severity_order.get(new_severity, 0) > severity_order.get(current_severity, 0):
        incident.severity = new_severity

