from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from models import (
    SensorData, SensorDataDB, FireRiskAnalysisDB,
    Alert, AlertDB, AlertStatus, User
)
from auth import get_current_active_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("/latest", response_model=SensorDataDB)
async def get_latest_sensor_data(current_user: User = Depends(get_current_active_user)):
    """Get the latest sensor reading"""
    db = get_database()
    
    sensor_data = await db.sensor_data.find_one(
        sort=[("timestamp", -1)]
    )
    
    if not sensor_data:
        raise HTTPException(status_code=404, detail="No sensor data found")
    
    sensor_data["_id"] = str(sensor_data["_id"])
    return SensorDataDB(**sensor_data)


@router.get("/history", response_model=List[SensorDataDB])
async def get_sensor_history(
    hours: int = Query(default=24, ge=1, le=168),  # 1 hour to 1 week
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get sensor data history"""
    db = get_database()
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    cursor = db.sensor_data.find(
        {"timestamp": {"$gte": start_time}}
    ).sort("timestamp", -1).limit(limit)
    
    sensor_data_list = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        sensor_data_list.append(SensorDataDB(**doc))
    
    return sensor_data_list


@router.get("/statistics")
async def get_sensor_statistics(
    hours: int = Query(default=24, ge=1, le=168),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistical summary of sensor data"""
    db = get_database()
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_time}}},
        {
            "$group": {
                "_id": None,
                "avg_temperature": {"$avg": "$temperature"},
                "max_temperature": {"$max": "$temperature"},
                "min_temperature": {"$min": "$temperature"},
                "avg_humidity": {"$avg": "$humidity"},
                "max_smoke": {"$max": "$smoke_level"},
                "avg_smoke": {"$avg": "$smoke_level"},
                "total_readings": {"$sum": 1}
            }
        }
    ]
    
    result = await db.sensor_data.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "message": "No data available for the specified period",
            "hours": hours
        }
    
    stats = result[0]
    stats.pop("_id")
    stats["period_hours"] = hours
    
    return stats


@router.get("/ai-responses")
async def get_ai_responses(
    limit: int = Query(default=50, ge=1, le=500),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI risk analysis responses"""
    db = get_database()
    
    cursor = db.risk_analysis.find().sort("timestamp", -1).limit(limit)
    
    responses = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        responses.append(doc)
    
    return responses


@router.get("/records")
async def get_sensor_records(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    risk_level: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated sensor records with optional filtering"""
    db = get_database()
    
    # Build query filter
    query_filter = {}
    if risk_level:
        query_filter["risk_level"] = risk_level
    
    # Get total count
    total = await db.sensor_data.count_documents(query_filter)
    
    # Get paginated records
    cursor = db.sensor_data.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)
    
    records = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        records.append(doc)
    
    return {
        "records": records,
        "total": total,
        "skip": skip,
        "limit": limit
    }
