"""
Sensor Data Ingestion Service
Reads data from ESP32 serial port and sends to FastAPI backend
"""
import serial
import json
import time
import re
import asyncio
import httpx
from datetime import datetime
from typing import Optional
from config import settings
from database import get_database, connect_to_mongo
from models import SensorData, Alert, AlertStatus, RiskLevel, SprinklerStatus
from ai_agent import fire_risk_agent
from bson import ObjectId


class SensorDataIngestion:
    def __init__(self):
        self.serial_port = settings.serial_port
        self.baud_rate = settings.baud_rate
        self.ser = None
        self.db = None
        self.current_reading = {}
        
    def parse_sensor_line(self, line: str) -> Optional[dict]:
        """Parse a serial line of ESP32 data"""
        data = {}
        
        patterns = {
            "smoke_level": r"Smoke Level:\s*(\d+)",
            "temperature": r"Temperature:\s*([\d\.]+)",
            "humidity": r"Humidity:\s*([\d\.]+)",
            "rain_level": r"Rain Level \(sim\):\s*([\d\.]+)",
            "rain_detected": r"Rain Detected:\s*(Yes|No)",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                val = match.group(1)
                if val.replace('.', '', 1).isdigit():
                    data[key] = float(val) if '.' in val else int(val)
                else:
                    data[key] = val == "Yes"
        
        return data if data else None
    
    async def process_sensor_data(self, sensor_data: SensorData):
        """Process sensor data with AI analysis and automation"""
        try:
            # Run AI risk analysis
            analysis = await fire_risk_agent.analyze_fire_risk(sensor_data)
            
            print(f"\n📊 Risk Analysis:")
            print(f"   Score: {analysis.risk_score}/100")
            print(f"   Level: {analysis.risk_level.value.upper()}")
            print(f"   Reasoning: {analysis.reasoning}")
            print(f"   Sprinkler: {'ACTIVATE' if analysis.should_activate_sprinkler else 'STANDBY'}")
            
            # Store sensor data with risk assessment
            sensor_dict = sensor_data.dict()
            sensor_dict["fire_risk_score"] = analysis.risk_score
            sensor_dict["risk_level"] = analysis.risk_level
            
            result = await self.db.sensor_data.insert_one(sensor_dict)
            sensor_id = str(result.inserted_id)
            
            # Store risk analysis
            analysis_dict = analysis.dict()
            analysis_dict["sensor_data_id"] = sensor_id
            await self.db.risk_analysis.insert_one(analysis_dict)
            
            # Handle alerts
            await self.handle_alerts(sensor_data, analysis)
            
            # Handle sprinkler automation
            await self.handle_sprinkler_automation(analysis)
            
            # Broadcast update via WebSocket (if running in FastAPI context)
            await self.broadcast_update(sensor_data, analysis)
            
        except Exception as e:
            print(f"⚠️ Error processing sensor data: {e}")
    
    async def handle_alerts(self, sensor_data: SensorData, analysis):
        """Create alerts based on risk analysis"""
        if analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = {
                "title": f"{analysis.risk_level.value.upper()} Fire Risk Detected",
                "message": analysis.reasoning,
                "severity": analysis.risk_level,
                "status": AlertStatus.ACTIVE,
                "sensor_data": sensor_data.dict(),
                "timestamp": datetime.utcnow()
            }
            
            await self.db.alerts.insert_one(alert)
            print(f"🚨 ALERT CREATED: {alert['title']}")
    
    async def handle_sprinkler_automation(self, analysis):
        """Handle automatic sprinkler control"""
        # Get current sprinkler status
        current_status = await self.db.sprinkler_control.find_one(
            sort=[("timestamp", -1)]
        )
        
        # Only auto-control if not in manual override
        if not current_status or not current_status.get("manual_override", False):
            if analysis.should_activate_sprinkler:
                # Activate sprinklers
                control_data = {
                    "status": SprinklerStatus.ON,
                    "manual_override": False,
                    "activated_at": datetime.utcnow(),
                    "reason": f"Auto-activated: {analysis.reasoning}",
                    "timestamp": datetime.utcnow()
                }
                
                await self.db.sprinkler_control.insert_one(control_data)
                await self.db.sprinkler_logs.insert_one({
                    "action": SprinklerStatus.ON,
                    "user": "system",
                    "manual": False,
                    "reason": analysis.reasoning,
                    "timestamp": datetime.utcnow()
                })
                
                print("💦 SPRINKLERS ACTIVATED AUTOMATICALLY")
            elif current_status and current_status.get("status") == SprinklerStatus.ON:
                # Check if we should deactivate
                if analysis.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                    control_data = {
                        "status": SprinklerStatus.AUTO,
                        "manual_override": False,
                        "deactivated_at": datetime.utcnow(),
                        "reason": "Auto-deactivated: Risk level decreased",
                        "timestamp": datetime.utcnow()
                    }
                    
                    await self.db.sprinkler_control.insert_one(control_data)
                    print("✅ Sprinklers deactivated - Risk decreased")
    
    async def broadcast_update(self, sensor_data: SensorData, analysis):
        """Broadcast updates to connected WebSocket clients"""
        try:
            # This would require access to the WebSocket manager
            # For now, we'll store it for the API to retrieve
            update = {
                "type": "sensor_update",
                "data": {
                    "temperature": sensor_data.temperature,
                    "humidity": sensor_data.humidity,
                    "smoke_level": sensor_data.smoke_level,
                    "risk_score": analysis.risk_score,
                    "risk_level": analysis.risk_level,
                    "timestamp": sensor_data.timestamp.isoformat()
                }
            }
            # Store in a temporary collection for API to retrieve
            await self.db.realtime_updates.insert_one(update)
        except Exception as e:
            print(f"⚠️ Broadcast error: {e}")
    
    async def run(self):
        """Main run loop"""
        print(f"🔌 Connecting to {self.serial_port} at {self.baud_rate} baud...")
        
        # Connect to database
        await connect_to_mongo()
        self.db = get_database()
        
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for ESP32 to stabilize
            print("✅ Connected! Listening for sensor data...\n")
        except serial.SerialException as e:
            print(f"❌ Serial connection failed: {e}")
            return
        
        while True:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                
                # Parse the sensor line
                data = self.parse_sensor_line(line)
                if data:
                    # Accumulate data (ESP32 sends each sensor on separate line)
                    self.current_reading.update(data)
                    
                    # Check if we have a complete reading
                    required_fields = ['temperature', 'humidity', 'smoke_level', 'rain_level', 'rain_detected']
                    if all(field in self.current_reading for field in required_fields):
                        # Create SensorData object
                        sensor_data = SensorData(
                            temperature=float(self.current_reading['temperature']),
                            humidity=float(self.current_reading['humidity']),
                            smoke_level=float(self.current_reading['smoke_level']),
                            rain_level=float(self.current_reading['rain_level']),
                            rain_detected=bool(self.current_reading['rain_detected']),
                            timestamp=datetime.utcnow()
                        )
                        
                        # Process the data
                        await self.process_sensor_data(sensor_data)
                        
                        # Reset for next reading
                        self.current_reading = {}
                
            except KeyboardInterrupt:
                print("\n🛑 Stopped by user.")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                await asyncio.sleep(1)
        
        if self.ser:
            self.ser.close()
        print("🔒 Serial connection closed.")


async def main():
    """Main entry point"""
    ingestion = SensorDataIngestion()
    await ingestion.run()


if __name__ == "__main__":
    asyncio.run(main())
