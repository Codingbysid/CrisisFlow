from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportRead
from app.services.ai_processor import process_report, process_report_with_llm
from app.services.clustering import find_nearby_incident, update_incident_with_report
from app.services.twitter_integration import search_disaster_tweets, monitor_twitter_stream
from app.services.sms_integration import receive_sms_webhook
from app.api.websocket import broadcast_new_report
from typing import List

router = APIRouter()


@router.post("/twitter/ingest/")
async def ingest_twitter_reports(
    query: str = "disaster OR fire OR flood",
    max_results: int = 10,
    provider: str = "dummy",
    db: Session = Depends(get_db)
):
    """
    Ingest disaster reports from Twitter
    
    Args:
        query: Twitter search query
        max_results: Maximum number of tweets to process
        provider: AI provider for processing
        db: Database session
    """
    tweets = search_disaster_tweets(query, max_results)
    
    if not tweets:
        return {"message": "No tweets found or Twitter not configured", "processed": 0}
    
    processed_count = 0
    reports = []
    
    for tweet in tweets:
        try:
            # Process tweet text
            if provider in ["openai", "gemini"]:
                try:
                    from app.services.ai_processor import process_report_with_llm
                    processed_data = await process_report_with_llm(tweet["text"], provider=provider)
                except:
                    processed_data = process_report(tweet["text"])
            else:
                processed_data = process_report(tweet["text"])
            
            # Check for nearby incident
            nearby_incident = find_nearby_incident(
                latitude=processed_data.get("latitude"),
                longitude=processed_data.get("longitude"),
                hazard_type=processed_data.get("hazard_type"),
                db=db,
                radius_meters=500.0
            )
            
            if nearby_incident:
                update_incident_with_report(nearby_incident, processed_data)
                incident_id = nearby_incident.id
            else:
                from app.models.incident import Incident
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
                db.flush()
                incident_id = new_incident.id
            
            # Create report
            db_report = Report(
                raw_text=f"[Twitter] {tweet['text']}",
                location=processed_data.get("location"),
                latitude=processed_data.get("latitude"),
                longitude=processed_data.get("longitude"),
                hazard_type=processed_data.get("hazard_type"),
                severity=processed_data.get("severity"),
                confidence_score=processed_data.get("confidence_score"),
                is_verified=False,
                incident_id=incident_id
            )
            
            db.add(db_report)
            reports.append(db_report)
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing tweet: {e}")
            continue
    
    db.commit()
    
    # Broadcast new reports
    for report in reports:
        db.refresh(report)
        await broadcast_new_report({
            "id": report.id,
            "raw_text": report.raw_text,
            "location": report.location,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "hazard_type": report.hazard_type,
            "severity": report.severity,
            "confidence_score": report.confidence_score,
            "timestamp": report.timestamp.isoformat() if report.timestamp else None,
            "is_verified": report.is_verified
        })
    
    return {"message": f"Processed {processed_count} tweets", "processed": processed_count}


@router.post("/sms/webhook/")
async def sms_webhook(
    request_data: dict,
    provider: str = "dummy",
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for receiving SMS reports via Twilio
    """
    sms_data = receive_sms_webhook(request_data)
    
    # Process SMS text
    if provider in ["openai", "gemini"]:
        try:
            from app.services.ai_processor import process_report_with_llm
            processed_data = await process_report_with_llm(sms_data["raw_text"], provider=provider)
        except:
            processed_data = process_report(sms_data["raw_text"])
    else:
        processed_data = process_report(sms_data["raw_text"])
    
    # Check for nearby incident
    nearby_incident = find_nearby_incident(
        latitude=processed_data.get("latitude"),
        longitude=processed_data.get("longitude"),
        hazard_type=processed_data.get("hazard_type"),
        db=db,
        radius_meters=500.0
    )
    
    if nearby_incident:
        update_incident_with_report(nearby_incident, processed_data)
        incident_id = nearby_incident.id
    else:
        from app.models.incident import Incident
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
        db.flush()
        incident_id = new_incident.id
    
    # Create report
    db_report = Report(
        raw_text=f"[SMS] {sms_data['raw_text']}",
        location=processed_data.get("location"),
        latitude=processed_data.get("latitude"),
        longitude=processed_data.get("longitude"),
        hazard_type=processed_data.get("hazard_type"),
        severity=processed_data.get("severity"),
        confidence_score=processed_data.get("confidence_score"),
        is_verified=False,
        incident_id=incident_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Broadcast
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
    
    return {"message": "SMS report processed", "report_id": db_report.id}

