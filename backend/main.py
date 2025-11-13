from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import json
from datetime import datetime

from database import connect_to_mongo, close_mongo_connection, get_database
from routes_auth import router as auth_router
from routes_sensors import router as sensors_router
from routes_alerts import router as alerts_router
from routes_sprinkler import router as sprinkler_router
from routes_dashboard import router as dashboard_router
from routes_export import router as export_router
from routes_advanced import router as advanced_router
from routes_sms import router as sms_router
from config import settings
from ml_predictor import predictor


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ Error sending to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Auto-train ML model if data exists
    try:
        print("\n" + "="*60)
        print("🤖 Checking ML Model Status...")
        print("="*60)
        
        if not predictor.is_trained:
            print("⚠️ ML model not trained. Attempting auto-training...")
            db = get_database()
            sensor_count = await db.sensor_data.count_documents({})
            
            if sensor_count >= 100:
                print(f"📊 Found {sensor_count} sensor readings. Training model...")
                
                # Get training data
                sensor_data = await db.sensor_data.find().sort("timestamp", -1).limit(10000).to_list(10000)
                
                sensor_history = [
                    {
                        'temperature': s.get('temperature', 25),
                        'humidity': s.get('humidity', 50),
                        'smoke_level': s.get('smoke_level', 0),
                        'rain_level': s.get('rain_level', 0),
                        'timestamp': s.get('timestamp')
                    }
                    for s in sensor_data
                ]
                
                risk_scores = [s.get('fire_risk_score', 30) for s in sensor_data]
                risk_levels = [s.get('risk_level', 'low') for s in sensor_data]
                
                # Train the model
                success = predictor.train(sensor_history, risk_scores, risk_levels)
                
                if success:
                    print("✅ ML model trained successfully on startup!")
                    print(f"   Training samples: {len(sensor_history)}")
                else:
                    print("❌ ML model training failed")
            else:
                print(f"⚠️ Not enough data to train ({sensor_count}/100 samples)")
                print("   Using mock predictions until sufficient data is collected")
        else:
            print("✅ ML model already trained and loaded")
            print(f"   Model path: {predictor.model_path}")
        
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error during ML model initialization: {e}")
        print("   Continuing with mock predictions...")
    
    yield
    # Shutdown
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Smart Forest Fire Prevention System",
    description="AI + IoT-based fire prevention system with ESP32, DHT22, and MQ-2 sensors",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(sensors_router)
app.include_router(alerts_router)
app.include_router(sprinkler_router)
app.include_router(dashboard_router)
app.include_router(export_router)
app.include_router(advanced_router)  # New advanced features
app.include_router(sms_router)  # SMS notification management


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Forest Fire Prevention System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = get_database()
    try:
        # Test database connection
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }


@app.post("/api/broadcast")
async def broadcast_sensor_data(data: dict):
    """Broadcast sensor data to all WebSocket clients"""
    await manager.broadcast(data)
    return {"status": "broadcasted"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Echo back for now (can be extended for client commands)
            await websocket.send_json({
                "type": "ack",
                "message": "Connected to real-time updates",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Export manager for use in other modules
def get_connection_manager():
    return manager


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
