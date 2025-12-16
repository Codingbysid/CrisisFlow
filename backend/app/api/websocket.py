from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
from app.database import SessionLocal
from app.models.report import Report
from app.models.incident import Incident
from sqlalchemy.orm import Session

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Skip disconnected clients
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/reports")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time report updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        db = SessionLocal()
        try:
            reports = db.query(Report).order_by(Report.timestamp.desc()).limit(50).all()
            incidents = db.query(Incident).filter(Incident.is_active == True).all()
            
            await websocket.send_json({
                "type": "initial_data",
                "reports": [
                    {
                        "id": r.id,
                        "raw_text": r.raw_text,
                        "location": r.location,
                        "latitude": r.latitude,
                        "longitude": r.longitude,
                        "hazard_type": r.hazard_type,
                        "severity": r.severity,
                        "confidence_score": r.confidence_score,
                        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                        "is_verified": r.is_verified
                    }
                    for r in reports
                ],
                "incidents": [
                    {
                        "id": i.id,
                        "location": i.location,
                        "latitude": i.latitude,
                        "longitude": i.longitude,
                        "hazard_type": i.hazard_type,
                        "severity": i.severity,
                        "confidence_score": i.confidence_score,
                        "witness_count": i.witness_count,
                        "is_active": i.is_active
                    }
                    for i in incidents
                ]
            })
        finally:
            db.close()
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "pong", "message": "Connection alive"})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_new_report(report_data: dict):
    """Broadcast a new report to all connected clients"""
    await manager.broadcast({
        "type": "new_report",
        "data": report_data
    })


async def broadcast_new_incident(incident_data: dict):
    """Broadcast a new incident to all connected clients"""
    await manager.broadcast({
        "type": "new_incident",
        "data": incident_data
    })

