"""
Database Alert Monitor
Continuously monitors database for sensor readings that exceed thresholds
and triggers SMS alerts
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from smart_alerts import alert_system


class DatabaseAlertMonitor:
    """
    Monitors database for new sensor readings and triggers alerts
    based on threshold conditions
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.is_running = False
        self.last_checked_timestamp: Optional[datetime] = None
        self.check_interval = 10  # Check every 10 seconds
        
        print("🔍 Database Alert Monitor initialized")
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.database_name]
        print(f"✅ Monitor connected to MongoDB: {settings.database_name}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("🔒 Monitor disconnected from MongoDB")
    
    async def get_latest_reading(self) -> Optional[Dict]:
        """Get the most recent sensor reading from database"""
        try:
            # Get the latest record
            cursor = self.db.sensor_data.find().sort("timestamp", -1).limit(1)
            
            async for doc in cursor:
                return {
                    'timestamp': doc.get('timestamp'),
                    'temperature': doc.get('temperature', 0),
                    'humidity': doc.get('humidity', 0),
                    'smoke_level': doc.get('smoke_level', 0),
                    'rain_level': doc.get('rain_level', 0),
                    'fire_risk_score': doc.get('fire_risk_score', 0),
                    'risk_level': doc.get('risk_level', 'unknown'),
                    'rain_detected': doc.get('rain_detected', False)
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching latest reading: {e}")
            return None
    
    async def check_thresholds(self, reading: Dict) -> bool:
        """
        Check if reading exceeds alert thresholds
        Returns True if alert should be triggered
        """
        risk_score = reading.get('fire_risk_score', 0)
        smoke_level = reading.get('smoke_level', 0)
        
        # Check risk threshold
        risk_exceeded = risk_score >= settings.sms_risk_threshold
        
        # Check smoke threshold
        smoke_exceeded = smoke_level >= settings.sms_smoke_threshold
        
        if risk_exceeded or smoke_exceeded:
            print(f"\n⚠️ THRESHOLD EXCEEDED!")
            print(f"   Risk Score: {risk_score}% (Threshold: {settings.sms_risk_threshold}%) {'✗ EXCEEDED' if risk_exceeded else '✓ OK'}")
            print(f"   Smoke Level: {smoke_level} (Threshold: {settings.sms_smoke_threshold}) {'✗ EXCEEDED' if smoke_exceeded else '✓ OK'}")
            return True
        
        return False
    
    async def process_reading(self, reading: Dict):
        """Process a sensor reading and trigger alerts if needed"""
        timestamp = reading.get('timestamp')
        
        # Skip if we've already processed this timestamp
        if self.last_checked_timestamp and timestamp <= self.last_checked_timestamp:
            return
        
        print(f"\n📊 Processing reading from {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Risk: {reading.get('fire_risk_score', 0)}%, "
              f"Smoke: {reading.get('smoke_level', 0)}, "
              f"Temp: {reading.get('temperature', 0)}°C")
        
        # Check if thresholds are exceeded
        if await self.check_thresholds(reading):
            print(f"🚨 Triggering alert evaluation...")
            
            # Trigger alert system
            alerts = await alert_system.evaluate_rules(reading)
            
            if alerts:
                print(f"✅ {len(alerts)} alert(s) triggered and sent!")
                for alert in alerts:
                    print(f"   - {alert.title} ({alert.priority.value})")
            else:
                print("⏳ No alerts sent (cooldown period active)")
        else:
            print("✓ Readings within safe thresholds")
        
        # Update last checked timestamp
        self.last_checked_timestamp = timestamp
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("🔍 Starting Database Alert Monitor")
        print("="*60)
        print(f"Check Interval: {self.check_interval} seconds")
        print(f"Risk Threshold: {settings.sms_risk_threshold}%")
        print(f"Smoke Threshold: {settings.sms_smoke_threshold}")
        print(f"SMS Recipients: {settings.sms_recipients}")
        print("="*60 + "\n")
        
        self.is_running = True
        
        while self.is_running:
            try:
                # Get latest reading
                reading = await self.get_latest_reading()
                
                if reading:
                    await self.process_reading(reading)
                else:
                    print("⚠️ No sensor data found in database")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def start(self):
        """Start the monitoring service"""
        await self.connect()
        await self.monitor_loop()
    
    async def stop(self):
        """Stop the monitoring service"""
        print("\n🛑 Stopping Database Alert Monitor...")
        self.is_running = False
        await self.disconnect()


# Global monitor instance
alert_monitor = DatabaseAlertMonitor()


async def start_alert_monitor():
    """Start the alert monitor service"""
    await alert_monitor.start()


async def stop_alert_monitor():
    """Stop the alert monitor service"""
    await alert_monitor.stop()


if __name__ == "__main__":
    """Run the monitor as a standalone service"""
    print("\n" + "="*60)
    print("📱 Database Alert Monitor - Standalone Mode")
    print("="*60)
    
    try:
        asyncio.run(start_alert_monitor())
    except KeyboardInterrupt:
        print("\n\n⚠️ Received interrupt signal")
        asyncio.run(stop_alert_monitor())
        print("👋 Monitor stopped")
