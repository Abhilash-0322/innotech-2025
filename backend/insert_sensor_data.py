#!/usr/bin/env python3
"""
Manual Sensor Data Inserter
Insert sensor readings into the database to trigger SMS alerts
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


async def insert_sensor_reading(
    temperature: float,
    humidity: float,
    smoke_level: float,
    rain_level: float = 0.0,
    fire_risk_score: float = None
):
    """
    Insert a sensor reading into the database
    This will be picked up by the alert monitor
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Calculate risk score if not provided
    if fire_risk_score is None:
        # Simple risk calculation
        temp_risk = (temperature - 20) * 2 if temperature > 20 else 0
        humidity_risk = (100 - humidity) * 0.5 if humidity < 70 else 0
        smoke_risk = (smoke_level / 4000) * 100
        fire_risk_score = min(100, temp_risk + humidity_risk + smoke_risk)
    
    # Determine risk level
    if fire_risk_score >= 75:
        risk_level = "critical"
    elif fire_risk_score >= 60:
        risk_level = "high"
    elif fire_risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Create sensor data document
    sensor_data = {
        "timestamp": datetime.utcnow(),
        "temperature": temperature,
        "humidity": humidity,
        "smoke_level": smoke_level,
        "rain_level": rain_level,
        "rain_detected": rain_level > 50,
        "fire_risk_score": fire_risk_score,
        "risk_level": risk_level
    }
    
    # Insert into database
    result = await db.sensor_data.insert_one(sensor_data)
    
    print(f"\n✅ Sensor reading inserted!")
    print(f"   ID: {result.inserted_id}")
    print(f"   Timestamp: {sensor_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Temperature: {temperature}°C")
    print(f"   Humidity: {humidity}%")
    print(f"   Smoke Level: {smoke_level}")
    print(f"   Fire Risk Score: {fire_risk_score:.1f}%")
    print(f"   Risk Level: {risk_level.upper()}")
    
    # Check if this should trigger alerts
    risk_alert = fire_risk_score >= settings.sms_risk_threshold
    smoke_alert = smoke_level >= settings.sms_smoke_threshold
    
    if risk_alert or smoke_alert:
        print(f"\n🚨 THIS READING EXCEEDS THRESHOLDS!")
        if risk_alert:
            print(f"   ⚠️ Risk Score ({fire_risk_score:.1f}%) >= Threshold ({settings.sms_risk_threshold}%)")
        if smoke_alert:
            print(f"   ⚠️ Smoke Level ({smoke_level}) >= Threshold ({settings.sms_smoke_threshold})")
        print(f"   📱 Alert monitor will send SMS within {db.sensor_data} seconds...")
    else:
        print(f"\n✓ Reading within safe thresholds")
    
    client.close()
    return sensor_data


async def insert_safe_reading():
    """Insert a safe reading"""
    print("\n" + "="*60)
    print("✓ Inserting SAFE reading...")
    print("="*60)
    
    await insert_sensor_reading(
        temperature=25.0,
        humidity=60.0,
        smoke_level=500.0,
        fire_risk_score=30.0
    )


async def insert_high_smoke_reading():
    """Insert a high smoke reading that will trigger alert"""
    print("\n" + "="*60)
    print("🔥 Inserting HIGH SMOKE reading...")
    print("="*60)
    
    await insert_sensor_reading(
        temperature=28.0,
        humidity=50.0,
        smoke_level=3500.0,  # Exceeds smoke threshold
        fire_risk_score=65.0
    )


async def insert_critical_risk_reading():
    """Insert a critical risk reading that will trigger alert"""
    print("\n" + "="*60)
    print("🚨 Inserting CRITICAL RISK reading...")
    print("="*60)
    
    await insert_sensor_reading(
        temperature=38.0,
        humidity=20.0,
        smoke_level=3800.0,
        fire_risk_score=88.0  # Exceeds risk threshold
    )


async def insert_custom_reading():
    """Insert a custom reading with user input"""
    print("\n" + "="*60)
    print("📝 Insert Custom Reading")
    print("="*60)
    
    try:
        temp = float(input("Temperature (°C): "))
        humidity = float(input("Humidity (%): "))
        smoke = float(input("Smoke Level: "))
        
        await insert_sensor_reading(
            temperature=temp,
            humidity=humidity,
            smoke_level=smoke
        )
    except ValueError:
        print("❌ Invalid input. Please enter numbers only.")


async def main():
    """Main menu"""
    print("\n" + "="*60)
    print("📊 Manual Sensor Data Inserter")
    print("="*60)
    print(f"Database: {settings.database_name}")
    print(f"Risk Threshold: {settings.sms_risk_threshold}%")
    print(f"Smoke Threshold: {settings.sms_smoke_threshold}")
    print(f"SMS Recipients: {settings.sms_recipients}")
    print("="*60)
    
    print("\nChoose an option:")
    print("1. Insert SAFE reading (no alert)")
    print("2. Insert HIGH SMOKE reading (⚠️ will trigger SMS)")
    print("3. Insert CRITICAL RISK reading (🚨 will trigger SMS)")
    print("4. Insert CUSTOM reading")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ")
    
    if choice == "1":
        await insert_safe_reading()
    elif choice == "2":
        await insert_high_smoke_reading()
    elif choice == "3":
        await insert_critical_risk_reading()
    elif choice == "4":
        await insert_custom_reading()
    elif choice == "5":
        print("\n👋 Exiting...")
        return
    else:
        print("\n❌ Invalid choice")
    
    print("\n" + "="*60)
    print("✅ Done! The alert monitor will process this reading.")
    print("   Check the backend logs for alert notifications.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
