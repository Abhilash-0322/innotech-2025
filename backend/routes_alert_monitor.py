"""
Alert Monitor Control API
Endpoints to control and monitor the database alert monitoring service
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from alert_monitor import alert_monitor
from config import settings


router = APIRouter(prefix="/alert-monitor", tags=["Alert Monitor"])


class MonitorStatus(BaseModel):
    """Monitor status response"""
    is_running: bool
    check_interval: int
    last_checked: Optional[datetime]
    risk_threshold: float
    smoke_threshold: float
    sms_recipients: str


class MonitorConfig(BaseModel):
    """Monitor configuration"""
    check_interval: Optional[int] = None


@router.get("/status", response_model=MonitorStatus)
async def get_monitor_status():
    """
    Get current status of the alert monitor
    """
    return MonitorStatus(
        is_running=alert_monitor.is_running,
        check_interval=alert_monitor.check_interval,
        last_checked=alert_monitor.last_checked_timestamp,
        risk_threshold=settings.sms_risk_threshold,
        smoke_threshold=settings.sms_smoke_threshold,
        sms_recipients=settings.sms_recipients
    )


@router.post("/config")
async def update_monitor_config(config: MonitorConfig):
    """
    Update monitor configuration
    """
    if config.check_interval is not None:
        if config.check_interval < 5:
            raise HTTPException(
                status_code=400,
                detail="Check interval must be at least 5 seconds"
            )
        alert_monitor.check_interval = config.check_interval
    
    return {
        "message": "Monitor configuration updated",
        "check_interval": alert_monitor.check_interval
    }


@router.post("/trigger-check")
async def trigger_manual_check():
    """
    Manually trigger a database check for alerts
    """
    if not alert_monitor.is_running:
        raise HTTPException(
            status_code=400,
            detail="Alert monitor is not running"
        )
    
    # Get latest reading and process it
    reading = await alert_monitor.get_latest_reading()
    
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No sensor data found in database"
        )
    
    # Force process even if already checked
    original_timestamp = alert_monitor.last_checked_timestamp
    alert_monitor.last_checked_timestamp = None
    
    await alert_monitor.process_reading(reading)
    
    # Restore if needed
    if alert_monitor.last_checked_timestamp is None:
        alert_monitor.last_checked_timestamp = original_timestamp
    
    return {
        "message": "Manual check completed",
        "reading": reading,
        "timestamp": reading.get('timestamp')
    }


@router.get("/latest-reading")
async def get_latest_reading():
    """
    Get the latest sensor reading from database
    """
    reading = await alert_monitor.get_latest_reading()
    
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No sensor data found in database"
        )
    
    # Check thresholds
    exceeds_threshold = await alert_monitor.check_thresholds(reading)
    
    return {
        "reading": reading,
        "exceeds_threshold": exceeds_threshold,
        "thresholds": {
            "risk": settings.sms_risk_threshold,
            "smoke": settings.sms_smoke_threshold
        }
    }
