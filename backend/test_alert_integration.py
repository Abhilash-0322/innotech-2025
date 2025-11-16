#!/usr/bin/env python3
"""
Test Alert System Integration
Simulates sensor data and tests if SMS alerts are triggered
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_alerts import alert_system


async def test_alert_trigger():
    """Test if alerts trigger with high risk data"""
    print("="*60)
    print("🧪 TESTING ALERT SYSTEM")
    print("="*60)
    
    print(f"\n⚙️ Current Thresholds:")
    print(f"   Risk Score: {alert_system.sms_risk_threshold}%")
    print(f"   Smoke Level: {alert_system.sms_smoke_threshold}")
    
    # Simulate sensor data with HIGH fire risk
    test_data = {
        'fire_risk_score': 85.0,  # High risk!
        'temperature': 38.5,
        'humidity': 22.0,
        'smoke_level': 3200,  # High smoke!
        'rain_level': 0
    }
    
    print(f"\n📊 Simulated Sensor Data:")
    print(f"   Fire Risk Score: {test_data['fire_risk_score']}%")
    print(f"   Temperature: {test_data['temperature']}°C")
    print(f"   Humidity: {test_data['humidity']}%")
    print(f"   Smoke Level: {test_data['smoke_level']} ⚠️ ABOVE THRESHOLD!")
    
    # Evaluate rules (this should trigger SMS if configured correctly)
    print(f"\n🔥 Evaluating alert rules...")
    triggered_alerts = await alert_system.evaluate_rules(test_data)
    
    if triggered_alerts:
        print(f"\n✅ SUCCESS! {len(triggered_alerts)} alert(s) triggered:")
        for alert in triggered_alerts:
            print(f"   - {alert.title} [{alert.priority.value.upper()}]")
            print(f"     Channels: {[ch.value for ch in alert.channels]}")
            print(f"     SMS will be sent to: {alert_system.sms_recipients}")
    else:
        print(f"\n❌ NO ALERTS TRIGGERED!")
        print(f"   Check your SMS_RISK_THRESHOLD in .env file")
        print(f"   Current threshold: {alert_system.sms_risk_threshold}%")
    
    print("\n" + "="*60)


async def test_low_risk():
    """Test with low risk data (should NOT trigger)"""
    print("\n" + "="*60)
    print("🧪 TESTING LOW RISK (Should NOT trigger)")
    print("="*60)
    
    test_data = {
        'fire_risk_score': 0.5,  # Very low risk
        'temperature': 25.0,
        'humidity': 60.0,
        'smoke_level': 50,
        'rain_level': 100
    }
    
    print(f"\n📊 Simulated Sensor Data:")
    print(f"   Fire Risk Score: {test_data['fire_risk_score']}%")
    
    triggered_alerts = await alert_system.evaluate_rules(test_data)
    
    if triggered_alerts:
        print(f"\n⚠️ Unexpected: {len(triggered_alerts)} alert(s) triggered (should be 0)")
    else:
        print(f"\n✅ Correct: No alerts triggered for low risk")
    
    print("="*60)


async def test_smoke_threshold():
    """Test smoke level threshold specifically"""
    print("\n" + "="*60)
    print(f"🧪 TESTING SMOKE THRESHOLD ({alert_system.sms_smoke_threshold})")
    print("="*60)
    
    test_data = {
        'fire_risk_score': 10.0,  # Low risk
        'temperature': 28.0,
        'humidity': 50.0,
        'smoke_level': alert_system.sms_smoke_threshold + 100,  # Just above threshold
        'rain_level': 0
    }
    
    print(f"\n📊 Simulated Sensor Data:")
    print(f"   Fire Risk Score: {test_data['fire_risk_score']}% (LOW)")
    print(f"   Smoke Level: {test_data['smoke_level']} ⚠️ ABOVE THRESHOLD!")
    print(f"   Should trigger SMS based on smoke alone")
    
    triggered_alerts = await alert_system.evaluate_rules(test_data)
    
    if triggered_alerts:
        print(f"\n✅ Smoke alert triggered: {len(triggered_alerts)} alert(s)")
        for alert in triggered_alerts:
            print(f"   - {alert.title}")
            if NotificationChannel.SMS in alert.channels:
                print(f"     ✅ SMS channel included")
    else:
        print(f"\n❌ No alert triggered for high smoke")
    
    print("="*60)


async def main():
    """Run all tests"""
    print("\n🚀 Starting Alert System Integration Tests\n")
    
    # Test 1: High risk (should trigger)
    await test_alert_trigger()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test 2: Low risk (should NOT trigger)
    await test_low_risk()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test 3: Smoke threshold (should trigger based on smoke alone)
    await test_smoke_threshold()
    
    print("\n✅ All tests completed!\n")
    print("💡 Configuration Summary:")
    print(f"   🔥 Risk Score Threshold: {alert_system.sms_risk_threshold}%")
    print(f"   💨 Smoke Level Threshold: {alert_system.sms_smoke_threshold}")
    print(f"   📱 SMS Recipients: {len(alert_system.sms_recipients)}")
    print("\n💡 If alerts triggered but you didn't receive SMS:")
    print("   1. Check your phone number is verified in Twilio Console")
    print("   2. Check Twilio Console logs: https://console.twilio.com/us1/monitor/logs/sms")
    print("   3. Check your phone's spam/junk messages")
    print("   4. Try: python test_sms.py send +917880764235\n")


if __name__ == "__main__":
    asyncio.run(main())
