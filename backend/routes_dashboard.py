from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timedelta
from models import DashboardStats, RiskLevel, SprinklerStatus, User
from auth import get_current_active_user
from database import get_database

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive dashboard statistics"""
    db = get_database()
    
    # Get latest sensor reading
    latest_sensor = await db.sensor_data.find_one(sort=[("timestamp", -1)])
    
    if not latest_sensor:
        # Return default values if no data
        return DashboardStats(
            current_temperature=0.0,
            current_humidity=0.0,
            current_smoke=0.0,
            current_risk_level=RiskLevel.LOW,
            current_risk_score=0.0,
            active_alerts=0,
            sprinkler_status=SprinklerStatus.AUTO,
            total_readings_today=0,
            average_temp_today=0.0,
            max_risk_today=0.0
        )
    
    # Get active alerts count
    active_alerts_count = await db.alerts.count_documents({"status": "active"})
    
    # Get sprinkler status
    sprinkler = await db.sprinkler_control.find_one(sort=[("timestamp", -1)])
    sprinkler_status = sprinkler["status"] if sprinkler else SprinklerStatus.AUTO
    
    # Get today's statistics
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": today_start}}},
        {
            "$group": {
                "_id": None,
                "avg_temp": {"$avg": "$temperature"},
                "max_risk": {"$max": "$fire_risk_score"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    today_stats = await db.sensor_data.aggregate(pipeline).to_list(1)
    
    if today_stats:
        stats = today_stats[0]
        avg_temp_today = round(stats["avg_temp"], 2) if stats["avg_temp"] else 0.0
        max_risk_today = round(stats["max_risk"], 2) if stats["max_risk"] else 0.0
        total_readings = stats["count"]
    else:
        avg_temp_today = 0.0
        max_risk_today = 0.0
        total_readings = 0
    
    return DashboardStats(
        current_temperature=latest_sensor["temperature"],
        current_humidity=latest_sensor["humidity"],
        current_smoke=latest_sensor["smoke_level"],
        current_risk_level=latest_sensor.get("risk_level", RiskLevel.LOW),
        current_risk_score=latest_sensor.get("fire_risk_score", 0.0),
        active_alerts=active_alerts_count,
        sprinkler_status=sprinkler_status,
        total_readings_today=total_readings,
        average_temp_today=avg_temp_today,
        max_risk_today=max_risk_today
    )


@router.get("/chart-data")
async def get_chart_data(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user)
):
    """Get data for dashboard charts"""
    db = get_database()
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Sample data every N minutes based on time range
    if hours <= 6:
        sample_minutes = 5
    elif hours <= 24:
        sample_minutes = 15
    else:
        sample_minutes = 60
    
    cursor = db.sensor_data.find(
        {"timestamp": {"$gte": start_time}}
    ).sort("timestamp", 1)
    
    data_points = []
    last_timestamp = None
    
    async for doc in cursor:
        # Sample data to reduce payload
        if last_timestamp is None or (doc["timestamp"] - last_timestamp).seconds >= sample_minutes * 60:
            data_points.append({
                "timestamp": doc["timestamp"].isoformat(),
                "temperature": doc["temperature"],
                "humidity": doc["humidity"],
                "smoke_level": doc["smoke_level"],
                "risk_score": doc.get("fire_risk_score", 0),
                "risk_level": doc.get("risk_level", "low")
            })
            last_timestamp = doc["timestamp"]
    
    return {
        "data": data_points,
        "period_hours": hours,
        "sample_minutes": sample_minutes
    }


@router.get("/risk-analysis")
async def get_recent_risk_analysis(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent AI risk analyses"""
    db = get_database()
    
    cursor = db.risk_analysis.find().sort("timestamp", -1).limit(limit)
    
    analyses = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        analyses.append(doc)
    
    return analyses
