"""
Real-time Sensor Data Streaming Service
Reads ESP32 sensor data and broadcasts via WebSocket
"""
import asyncio
import serial
import re
import json
import httpx
from datetime import datetime
from typing import Optional
from config import settings
from database import get_database, connect_to_mongo, close_mongo_connection
from models import SensorData, RiskLevel
from ai_agent import fire_risk_agent


class SensorStreamer:
    def __init__(self):
        self.serial_port = settings.serial_port
        self.baud_rate = settings.baud_rate
        self.ser = None
        self.db = None
        self.current_reading = {}
        self.websocket_url = "http://localhost:8000"
        self.last_ai_analysis_time = None
        self.ai_analysis_interval = settings.ai_analysis_interval  # From config (default: 30 seconds)
        self.last_risk_score = 0
        self.last_risk_level = "low"
        
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
    
    async def broadcast_to_websocket(self, data: dict):
        """Broadcast sensor data to WebSocket clients via API"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.websocket_url}/api/broadcast",
                    json=data,
                    timeout=5.0
                )
        except Exception as e:
            print(f"⚠️ Failed to broadcast: {e}")
    
    async def process_sensor_data(self, sensor_data: SensorData, force_ai: bool = False):
        """Process and stream sensor data"""
        try:
            current_time = datetime.utcnow()
            should_run_ai = False
            
            # Check if we should run AI analysis
            if force_ai or self.last_ai_analysis_time is None:
                should_run_ai = True
            elif (current_time - self.last_ai_analysis_time).total_seconds() >= self.ai_analysis_interval:
                should_run_ai = True
            
            # Run AI risk analysis only if interval has passed
            if should_run_ai:
                analysis = await fire_risk_agent.analyze_fire_risk(sensor_data)
                self.last_ai_analysis_time = current_time
                self.last_risk_score = analysis.risk_score
                self.last_risk_level = analysis.risk_level.value
                
                print(f"\n📊 Live Sensor Data (🤖 AI ANALYSIS):")
                print(f"   🌡️  Temp: {sensor_data.temperature}°C")
                print(f"   💧 Humidity: {sensor_data.humidity}%")
                print(f"   💨 Smoke: {sensor_data.smoke_level}")
                print(f"   🌧️  Rain: {'Yes' if sensor_data.rain_detected else 'No'}")
                print(f"   🔥 Risk: {analysis.risk_level.value.upper()} ({analysis.risk_score}/100)")
                print(f"   🧠 AI Reasoning: {analysis.reasoning[:100]}...")
                
                # Store in database with AI analysis
                sensor_dict = sensor_data.dict()
                sensor_dict["fire_risk_score"] = analysis.risk_score
                sensor_dict["risk_level"] = analysis.risk_level.value
                
                result = await self.db.sensor_data.insert_one(sensor_dict)
                sensor_id = str(result.inserted_id)
                
                # Store risk analysis with AI response
                analysis_dict = analysis.dict()
                analysis_dict["sensor_data_id"] = sensor_id
                analysis_dict["ai_response"] = {
                    "risk_score": analysis.risk_score,
                    "risk_level": analysis.risk_level.value,
                    "reasoning": analysis.reasoning,
                    "recommendations": analysis.recommendations,
                    "should_activate_sprinkler": analysis.should_activate_sprinkler,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await self.db.risk_analysis.insert_one(analysis_dict)
                
                print(f"   💾 Saved with AI analysis (ID: {sensor_id})")
            else:
                # Use last AI analysis results
                print(f"\n📊 Live Sensor Data (using cached AI):")
                print(f"   🌡️  Temp: {sensor_data.temperature}°C")
                print(f"   💧 Humidity: {sensor_data.humidity}%")
                print(f"   💨 Smoke: {sensor_data.smoke_level}")
                print(f"   🌧️  Rain: {'Yes' if sensor_data.rain_detected else 'No'}")
                print(f"   🔥 Risk: {self.last_risk_level.upper()} ({self.last_risk_score}/100) [Cached]")
                
                # Store in database with last known risk assessment
                sensor_dict = sensor_data.dict()
                sensor_dict["fire_risk_score"] = self.last_risk_score
                sensor_dict["risk_level"] = self.last_risk_level
                
                result = await self.db.sensor_data.insert_one(sensor_dict)
                sensor_id = str(result.inserted_id)
                
                print(f"   💾 Saved with cached risk (ID: {sensor_id})")
                
                # Use cached analysis for broadcast
                analysis = type('obj', (object,), {
                    'risk_score': self.last_risk_score,
                    'risk_level': type('obj', (object,), {'value': self.last_risk_level}),
                    'recommendations': []
                })
            
            # Prepare broadcast message
            broadcast_data = {
                "type": "sensor_update",
                "data": {
                    "temperature": sensor_data.temperature,
                    "humidity": sensor_data.humidity,
                    "smoke_level": sensor_data.smoke_level,
                    "rain_level": sensor_data.rain_level,
                    "rain_detected": sensor_data.rain_detected,
                    "fire_risk_score": analysis.risk_score,
                    "risk_level": analysis.risk_level.value,
                    "timestamp": sensor_data.timestamp.isoformat(),
                    "recommendations": analysis.recommendations,
                }
            }
            
            # Broadcast to WebSocket clients
            await self.broadcast_to_websocket(broadcast_data)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error processing sensor data: {e}")
            import traceback
            traceback.print_exc()
    
    async def start_streaming(self):
        """Start reading and streaming sensor data"""
        print("🚀 Starting Sensor Data Stream...")
        print(f"📡 Port: {self.serial_port}")
        print(f"⚡ Baud Rate: {self.baud_rate}")
        print(f"🤖 AI Analysis Interval: Every {self.ai_analysis_interval} seconds")
        print(f"💡 Tip: Change ai_analysis_interval in code to adjust (recommended: 30-60 seconds)")
        print()
        
        # Connect to database
        await connect_to_mongo()
        self.db = get_database()
        
        try:
            # Open serial connection
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print("✅ Serial connection established")
            
            # Wait for serial to stabilize
            await asyncio.sleep(2)
            
            print("\n🔴 LIVE STREAMING - Press Ctrl+C to stop\n")
            print("=" * 60)
            
            while True:
                try:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        
                        if line:
                            # Parse sensor data
                            parsed = self.parse_sensor_line(line)
                            if parsed:
                                self.current_reading.update(parsed)
                                
                                # Check if we have a complete reading
                                required_keys = ["temperature", "humidity", "smoke_level", "rain_level", "rain_detected"]
                                if all(k in self.current_reading for k in required_keys):
                                    # Create sensor data object
                                    sensor_data = SensorData(
                                        temperature=self.current_reading["temperature"],
                                        humidity=self.current_reading["humidity"],
                                        smoke_level=self.current_reading["smoke_level"],
                                        rain_level=self.current_reading["rain_level"],
                                        rain_detected=self.current_reading["rain_detected"],
                                        timestamp=datetime.utcnow()
                                    )
                                    
                                    # Process and stream data
                                    await self.process_sensor_data(sensor_data)
                                    
                                    # Reset reading
                                    self.current_reading = {}
                    
                    await asyncio.sleep(0.1)
                    
                except serial.SerialException as e:
                    print(f"❌ Serial error: {e}")
                    await asyncio.sleep(5)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping sensor stream...")
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
            await close_mongo_connection()
            print("✅ Cleanup complete")


async def main():
    streamer = SensorStreamer()
    await streamer.start_streaming()


if __name__ == "__main__":
    asyncio.run(main())
