"""
SMS Configuration and Testing Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from auth import get_current_active_user
from models import User
from smart_alerts import alert_system, AlertMessage, AlertPriority
from datetime import datetime
import asyncio

router = APIRouter(prefix="/sms", tags=["SMS Notifications"])


class SMSConfig(BaseModel):
    """SMS Configuration Model"""
    recipients: List[str]  # List of phone numbers
    enabled: bool = True


class SMSTestRequest(BaseModel):
    """Request model for testing SMS"""
    phone_number: str
    message: str = "Test message from Forest Fire Prevention System"


class SMSStatusResponse(BaseModel):
    """SMS System Status"""
    configured: bool
    twilio_configured: bool
    recipients_count: int
    recipients: List[str]
    last_sms_sent: str = "Never"


@router.get("/status", response_model=SMSStatusResponse)
async def get_sms_status(current_user: User = Depends(get_current_active_user)):
    """Get SMS system configuration status"""
    
    twilio_configured = bool(
        alert_system.twilio_account_sid and 
        alert_system.twilio_auth_token and 
        alert_system.twilio_phone_number
    )
    
    return SMSStatusResponse(
        configured=twilio_configured and len(alert_system.sms_recipients) > 0,
        twilio_configured=twilio_configured,
        recipients_count=len(alert_system.sms_recipients),
        recipients=alert_system.sms_recipients
    )


@router.post("/config")
async def update_sms_config(
    config: SMSConfig,
    current_user: User = Depends(get_current_active_user)
):
    """Update SMS recipient configuration"""
    
    # Validate phone numbers (basic validation)
    for phone in config.recipients:
        if not phone.startswith('+'):
            raise HTTPException(
                status_code=400,
                detail=f"Phone number {phone} must start with country code (e.g., +91, +1)"
            )
        if len(phone) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Phone number {phone} appears to be invalid"
            )
    
    # Update recipients
    alert_system.sms_recipients = config.recipients
    
    return {
        "message": "SMS configuration updated successfully",
        "recipients_count": len(config.recipients),
        "recipients": config.recipients
    }


@router.post("/test")
async def test_sms(
    test_request: SMSTestRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Send a test SMS to verify configuration"""
    
    if not alert_system.twilio_account_sid or not alert_system.twilio_auth_token:
        raise HTTPException(
            status_code=400,
            detail="Twilio not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in environment variables"
        )
    
    if not alert_system.twilio_phone_number:
        raise HTTPException(
            status_code=400,
            detail="Twilio phone number not configured. Please set TWILIO_PHONE_NUMBER in environment variables"
        )
    
    try:
        from twilio.rest import Client
        
        client = Client(alert_system.twilio_account_sid, alert_system.twilio_auth_token)
        
        message = client.messages.create(
            body=test_request.message,
            from_=alert_system.twilio_phone_number,
            to=test_request.phone_number
        )
        
        return {
            "success": True,
            "message": "Test SMS sent successfully",
            "sid": message.sid,
            "to": test_request.phone_number,
            "status": message.status
        }
    
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Twilio library not installed. Run: pip install twilio"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send SMS: {str(e)}"
        )


@router.post("/test-alert")
async def test_alert_sms(current_user: User = Depends(get_current_active_user)):
    """Send a test fire alert SMS to all configured recipients"""
    
    if not alert_system.sms_recipients:
        raise HTTPException(
            status_code=400,
            detail="No SMS recipients configured"
        )
    
    # Create a mock alert for testing
    import uuid
    
    test_alert = AlertMessage(
        alert_id=f"TEST-{uuid.uuid4().hex[:8]}",
        title="TEST ALERT - Fire Risk Detected",
        message="This is a test alert from the Forest Fire Prevention System",
        priority=AlertPriority.HIGH,
        source="test_system",
        data={
            'fire_risk_score': 82.5,
            'temperature': 38.5,
            'humidity': 25.0,
            'smoke_level': 2800,
            'zone_id': 'Test Zone'
        },
        channels=[],
        timestamp=datetime.utcnow()
    )
    
    # Send SMS
    try:
        await alert_system._send_sms(test_alert)
        
        return {
            "success": True,
            "message": f"Test alert SMS sent to {len(alert_system.sms_recipients)} recipient(s)",
            "recipients": alert_system.sms_recipients,
            "alert_id": test_alert.alert_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test alert: {str(e)}"
        )


@router.get("/recipients")
async def get_recipients(current_user: User = Depends(get_current_active_user)):
    """Get list of configured SMS recipients"""
    return {
        "recipients": alert_system.sms_recipients,
        "count": len(alert_system.sms_recipients)
    }


@router.post("/recipients/add")
async def add_recipient(
    phone_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """Add a new SMS recipient"""
    
    # Validate phone number
    if not phone_number.startswith('+'):
        raise HTTPException(
            status_code=400,
            detail="Phone number must start with country code (e.g., +919876543210)"
        )
    
    if phone_number in alert_system.sms_recipients:
        raise HTTPException(
            status_code=400,
            detail="Phone number already exists in recipients list"
        )
    
    alert_system.sms_recipients.append(phone_number)
    
    return {
        "message": "Recipient added successfully",
        "phone_number": phone_number,
        "total_recipients": len(alert_system.sms_recipients)
    }


@router.delete("/recipients/{phone_number}")
async def remove_recipient(
    phone_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """Remove an SMS recipient"""
    
    if phone_number not in alert_system.sms_recipients:
        raise HTTPException(
            status_code=404,
            detail="Phone number not found in recipients list"
        )
    
    alert_system.sms_recipients.remove(phone_number)
    
    return {
        "message": "Recipient removed successfully",
        "phone_number": phone_number,
        "remaining_recipients": len(alert_system.sms_recipients)
    }
