#!/usr/bin/env python3
"""
Test SMS alerts with historical sensor data
"""
import asyncio
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from smart_alerts import alert_system


async def insert_test_sensor_data():
    """Insert test sensor data to simulate historical readings"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    print("\n📊 Inserting test sensor data into database...")
    
    # Create 3 historical readings showing increasing risk
    now = datetime.utcnow()
    test_data = [
        {
            "timestamp": now - timedelta(minutes=10),
            "temperature": 28.5,
            "humidity": 45.0,
            "smoke_level": 1500.0,
            "rain_level": 0.0,
            "rain_detected": False,
            "fire_risk_score": 55.0,
            "risk_level": "medium"
        },
        {
            "timestamp": now - timedelta(minutes=5),
            "temperature": 32.0,
            "humidity": 35.0,
            "smoke_level": 2200.0,
            "rain_level": 0.0,
            "rain_detected": False,
            "fire_risk_score": 68.0,
            "risk_level": "high"
        },
        {
            "timestamp": now,
            "temperature": 35.5,
            "humidity": 25.0,
            "smoke_level": 3200.0,
            "rain_level": 0.0,
            "rain_detected": False,
            "fire_risk_score": 85.0,
            "risk_level": "critical"
        }
    ]
    
    # Insert test data
    result = await db.sensor_data.insert_many(test_data)
    print(f"✅ Inserted {len(result.inserted_ids)} test records")
    
    # Show what was inserted
    print("\n📈 Historical Data (oldest to newest):")
    for i, data in enumerate(test_data, 1):
        print(f"  {i}. {data['timestamp'].strftime('%H:%M:%S')} - "
              f"Risk: {data['fire_risk_score']}%, "
              f"Smoke: {data['smoke_level']}, "
              f"Temp: {data['temperature']}°C")
    
    client.close()
    return test_data


async def test_sms_with_history():
    """Test SMS alert with historical data"""
    print("\n" + "="*60)
    print("🧪 Testing SMS Alert with Historical Sensor Data")
    print("="*60)
    
    # Insert test data first
    test_data = await insert_test_sensor_data()
    
    # Get the latest reading (critical alert)
    latest = test_data[-1]
    
    print(f"\n🔥 Triggering alert with current critical conditions:")
    print(f"   Risk Score: {latest['fire_risk_score']}%")
    print(f"   Smoke Level: {latest['smoke_level']}")
    print(f"   Temperature: {latest['temperature']}°C")
    
    # Simulate alert evaluation
    sensor_data = {
        'temperature': latest['temperature'],
        'humidity': latest['humidity'],
        'smoke_level': latest['smoke_level'],
        'fire_risk_score': latest['fire_risk_score'],
        'risk_level': latest['risk_level'],
        'timestamp': latest['timestamp']
    }
    
    print(f"\n📱 Evaluating alert rules and sending SMS...")
    alerts = await alert_system.evaluate_rules(sensor_data)
    
    if alerts:
        print(f"\n✅ {len(alerts)} alert(s) triggered!")
        for alert in alerts:
            print(f"   - {alert.title} ({alert.priority.value})")
            print(f"     Channels: {', '.join([c.value for c in alert.channels])}")
    else:
        print("\n⚠️ No alerts triggered (might be in cooldown)")
    
    print("\n" + "="*60)
    print("Check your phone for SMS with historical trend data!")
    print("="*60)


async def check_database_history():
    """Check what's currently in the database"""
    print("\n" + "="*60)
    print("📊 Checking Database for Historical Sensor Data")
    print("="*60)
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Get recent records
    cursor = db.sensor_data.find().sort("timestamp", -1).limit(5)
    records = []
    
    async for doc in cursor:
        records.append(doc)
    
    if records:
        print(f"\n✅ Found {len(records)} recent records:")
        for i, record in enumerate(records, 1):
            ts = record.get('timestamp', 'Unknown')
            risk = record.get('fire_risk_score', 0)
            smoke = record.get('smoke_level', 0)
            temp = record.get('temperature', 0)
            
            if isinstance(ts, datetime):
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            else:
                ts_str = str(ts)
            
            print(f"  {i}. {ts_str}")
            print(f"     Risk: {risk}%, Smoke: {smoke}, Temp: {temp}°C")
    else:
        print("\n⚠️ No sensor data found in database")
    
    client.close()
    print("="*60)


async def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        await check_database_history()
    else:
        await test_sms_with_history()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📱 SMS Alert with Historical Data - Test Script")
    print("="*60)
    print(f"SMS Recipients: {settings.sms_recipients}")
    print(f"Risk Threshold: {settings.sms_risk_threshold}%")
    print(f"Smoke Threshold: {settings.sms_smoke_threshold}")
    print("="*60)
    
    asyncio.run(main())
