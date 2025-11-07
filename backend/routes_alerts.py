from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
from models import Alert, AlertDB, AlertStatus, User
from auth import get_current_active_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertDB])
async def get_alerts(
    status: AlertStatus = Query(None),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user)
):
    """Get alerts with optional filtering"""
    db = get_database()
    
    query = {"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=hours)}}
    if status:
        query["status"] = status
    
    cursor = db.alerts.find(query).sort("timestamp", -1).limit(limit)
    
    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        alerts.append(AlertDB(**doc))
    
    return alerts


@router.get("/active", response_model=List[AlertDB])
async def get_active_alerts(current_user: User = Depends(get_current_active_user)):
    """Get all active alerts"""
    db = get_database()
    
    cursor = db.alerts.find({"status": AlertStatus.ACTIVE}).sort("timestamp", -1)
    
    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        alerts.append(AlertDB(**doc))
    
    return alerts


@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an alert"""
    db = get_database()
    
    result = await db.alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$set": {
                "status": AlertStatus.ACKNOWLEDGED,
                "acknowledged_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert acknowledged", "alert_id": alert_id}


@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Resolve an alert"""
    db = get_database()
    
    result = await db.alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$set": {
                "status": AlertStatus.RESOLVED,
                "resolved_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved", "alert_id": alert_id}


@router.get("/count")
async def get_alert_counts(current_user: User = Depends(get_current_active_user)):
    """Get count of alerts by status"""
    db = get_database()
    
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = await db.alerts.aggregate(pipeline).to_list(None)
    
    counts = {status.value: 0 for status in AlertStatus}
    for result in results:
        counts[result["_id"]] = result["count"]
    
    return counts
