from fastapi import APIRouter, Depends, HTTPException
from models import SprinklerControl, SprinklerControlDB, SprinklerStatus, User
from auth import get_current_active_user
from database import get_database
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/sprinkler", tags=["Sprinkler Control"])


@router.get("/status", response_model=SprinklerControlDB)
async def get_sprinkler_status(current_user: User = Depends(get_current_active_user)):
    """Get current sprinkler status"""
    db = get_database()
    
    status = await db.sprinkler_control.find_one(sort=[("timestamp", -1)])
    
    if not status:
        # Create default status
        default_status = {
            "status": SprinklerStatus.AUTO,
            "manual_override": False,
            "timestamp": datetime.utcnow()
        }
        result = await db.sprinkler_control.insert_one(default_status)
        default_status["_id"] = str(result.inserted_id)
        return SprinklerControlDB(**default_status)
    
    status["_id"] = str(status["_id"])
    return SprinklerControlDB(**status)


@router.post("/control")
async def control_sprinkler(
    action: SprinklerStatus,
    reason: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """Manually control sprinkler system"""
    db = get_database()
    
    control_data = {
        "status": action,
        "manual_override": True,
        "timestamp": datetime.utcnow(),
        "reason": reason or f"Manual override by {current_user.email}"
    }
    
    if action == SprinklerStatus.ON:
        control_data["activated_at"] = datetime.utcnow()
    elif action == SprinklerStatus.OFF:
        control_data["deactivated_at"] = datetime.utcnow()
    
    result = await db.sprinkler_control.insert_one(control_data)
    control_data["_id"] = str(result.inserted_id)
    
    # Log the action
    await db.sprinkler_logs.insert_one({
        "action": action,
        "user": current_user.email,
        "manual": True,
        "reason": reason,
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": f"Sprinkler system set to {action}",
        "control": SprinklerControlDB(**control_data)
    }


@router.post("/auto")
async def set_auto_mode(current_user: User = Depends(get_current_active_user)):
    """Set sprinkler to automatic mode"""
    db = get_database()
    
    control_data = {
        "status": SprinklerStatus.AUTO,
        "manual_override": False,
        "timestamp": datetime.utcnow(),
        "reason": f"Auto mode enabled by {current_user.email}"
    }
    
    result = await db.sprinkler_control.insert_one(control_data)
    control_data["_id"] = str(result.inserted_id)
    
    return {
        "message": "Sprinkler system set to automatic mode",
        "control": SprinklerControlDB(**control_data)
    }


@router.get("/history")
async def get_sprinkler_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get sprinkler control history"""
    db = get_database()
    
    cursor = db.sprinkler_logs.find().sort("timestamp", -1).limit(limit)
    
    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)
    
    return history
