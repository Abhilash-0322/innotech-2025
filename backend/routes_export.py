"""
Export Routes - CSV and data export functionality
"""
from fastapi import APIRouter, Depends, Query, Response
from datetime import datetime, timedelta
from database import get_database
from auth import get_current_active_user
from models import UserInDB
import csv
import io

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/sensor-data/csv")
async def export_sensor_data_csv(
    hours: int = Query(24, ge=1, le=720),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export sensor data as CSV"""
    db = get_database()
    
    # Get data from last N hours
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    cursor = db.sensor_data.find({
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", -1)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp',
        'Temperature (°C)',
        'Humidity (%)',
        'Smoke Level',
        'Rain Level',
        'Rain Detected',
        'Fire Risk Score',
        'Risk Level'
    ])
    
    # Write data
    count = 0
    async for record in cursor:
        writer.writerow([
            record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            f"{record['temperature']:.2f}",
            f"{record['humidity']:.2f}",
            record['smoke_level'],
            f"{record.get('rain_level', 0):.2f}",
            'Yes' if record.get('rain_detected', False) else 'No',
            f"{record.get('fire_risk_score', 0):.1f}",
            record.get('risk_level', 'unknown')
        ])
        count += 1
    
    # Create response
    output.seek(0)
    filename = f"sensor_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/ai-responses/csv")
async def export_ai_responses_csv(
    hours: int = Query(24, ge=1, le=720),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export AI risk analysis responses as CSV"""
    db = get_database()
    
    # Get data from last N hours
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    cursor = db.risk_analysis.find({
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", -1)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp',
        'Risk Score',
        'Risk Level',
        'Reasoning',
        'Recommendations',
        'Sprinkler Action',
        'Sensor Data ID'
    ])
    
    # Write data
    count = 0
    async for record in cursor:
        ai_response = record.get('ai_response', {})
        recommendations = '; '.join(record.get('recommendations', []))
        
        writer.writerow([
            record.get('timestamp', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S'),
            f"{record.get('risk_score', 0):.1f}",
            record.get('risk_level', 'unknown'),
            record.get('reasoning', 'N/A'),
            recommendations,
            'Yes' if record.get('should_activate_sprinkler', False) else 'No',
            record.get('sensor_data_id', 'N/A')
        ])
        count += 1
    
    # Create response
    output.seek(0)
    filename = f"ai_responses_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/alerts/csv")
async def export_alerts_csv(
    hours: int = Query(168, ge=1, le=720),  # Default 1 week
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export alerts as CSV"""
    db = get_database()
    
    # Get data from last N hours
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    cursor = db.alerts.find({
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", -1)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp',
        'Title',
        'Message',
        'Severity',
        'Status',
        'Acknowledged By'
    ])
    
    # Write data
    async for record in cursor:
        writer.writerow([
            record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            record.get('title', 'N/A'),
            record.get('message', 'N/A'),
            record.get('severity', 'N/A'),
            record.get('status', 'N/A'),
            record.get('acknowledged_by', 'N/A')
        ])
    
    # Create response
    output.seek(0)
    filename = f"alerts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
