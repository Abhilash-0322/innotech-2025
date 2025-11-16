# 🔥 Database-Based SMS Alert System Guide

## Overview

The system now continuously **monitors your database** for sensor readings and automatically sends SMS alerts when thresholds are exceeded. You can insert sensor data from your external system, and this system will handle the alerting.

---

## 🏗️ Architecture

```
External System → MongoDB Database → Alert Monitor → SMS via Twilio
                     (Sensor Data)      (Checks every 10s)   (Historical trend)
```

### Components:

1. **Alert Monitor** (`alert_monitor.py`)
   - Runs continuously in the background
   - Checks database every 10 seconds for new readings
   - Evaluates against thresholds
   - Triggers SMS alerts with historical data

2. **Smart Alert System** (`smart_alerts.py`)
   - Fetches recent 2-3 readings for trend analysis
   - Sends SMS with current + historical values
   - Manages cooldown periods to prevent spam

3. **Manual Data Inserter** (`insert_sensor_data.py`)
   - CLI tool to manually insert sensor readings
   - Useful for testing and manual data entry

---

## 🚀 Quick Start

### 1. Start the Backend (Monitor Runs Automatically)

```bash
cd backend
uvicorn main:app --reload
```

The alert monitor starts automatically and displays:
```
🔍 Starting Database Alert Monitor
Check Interval: 10 seconds
Risk Threshold: 75.0%
Smoke Threshold: 2500
```

### 2. Insert Sensor Data

**Option A: Using the Manual Inserter (Interactive)**
```bash
python3 insert_sensor_data.py
```

**Option B: Programmatically from Your External System**
```python
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def send_reading_to_alert_system():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["forest_fire_db"]
    
    await db.sensor_data.insert_one({
        "timestamp": datetime.utcnow(),
        "temperature": 35.0,
        "humidity": 25.0,
        "smoke_level": 3200,  # Exceeds threshold!
        "rain_level": 0.0,
        "rain_detected": False,
        "fire_risk_score": 85.0,
        "risk_level": "critical"
    })
```

**Option C: Via REST API Endpoint**
```bash
curl -X POST http://localhost:8000/sensors/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 35.0,
    "humidity": 25.0,
    "smoke_level": 3200,
    "rain_level": 0.0,
    "rain_detected": false
  }'
```

### 3. SMS Alert Sent!

Within 10 seconds, if thresholds are exceeded:

```
📱 SMS Example:
🚨 FIRE ALERT: Critical Fire Risk
CURRENT: Risk:85% Temp:35.0°C Smoke:3200
TREND:
14:30 R:85% S:3200
14:25 R:68% S:2200
14:20 R:55% S:1500
Time: 14:30:45
```

---

## 📊 Database Schema

Your sensor data should match this structure:

```json
{
  "timestamp": "2025-11-14T14:30:00Z",
  "temperature": 35.0,
  "humidity": 25.0,
  "smoke_level": 3200.0,
  "rain_level": 0.0,
  "rain_detected": false,
  "fire_risk_score": 85.0,
  "risk_level": "critical"
}
```

### Required Fields:
- `timestamp`: datetime (UTC)
- `temperature`: float (°C)
- `humidity`: float (%)
- `smoke_level`: float (sensor reading)
- `fire_risk_score`: float (0-100%)

---

## 🎛️ API Endpoints

### Check Monitor Status
```bash
curl http://localhost:8000/alert-monitor/status
```

Response:
```json
{
  "is_running": true,
  "check_interval": 10,
  "last_checked": "2025-11-14T14:30:45Z",
  "risk_threshold": 75.0,
  "smoke_threshold": 2500,
  "sms_recipients": "+917880764235"
}
```

### Get Latest Reading
```bash
curl http://localhost:8000/alert-monitor/latest-reading
```

### Manually Trigger Check
```bash
curl -X POST http://localhost:8000/alert-monitor/trigger-check
```

### Update Check Interval
```bash
curl -X POST http://localhost:8000/alert-monitor/config \
  -H "Content-Type: application/json" \
  -d '{"check_interval": 15}'
```

---

## ⚙️ Configuration

Edit `backend/.env`:

```bash
# Alert Thresholds
SMS_RISK_THRESHOLD=75.0
SMS_SMOKE_THRESHOLD=2500

# SMS Recipients (comma-separated)
SMS_RECIPIENTS=+917880764235,+918874789223

# Twilio Credentials
TWILIO_ACCOUNT_SID=ACxxxxx...
TWILIO_AUTH_TOKEN=xxxxx...
TWILIO_PHONE_NUMBER=+14144044646
```

---

## 🧪 Testing

### Test 1: Safe Reading (No Alert)
```bash
python3 insert_sensor_data.py
# Choose option 1
```

Expected: No SMS sent

### Test 2: High Smoke (Alert)
```bash
python3 insert_sensor_data.py
# Choose option 2
```

Expected: SMS with "Smoke Detection" alert

### Test 3: Critical Risk (Alert)
```bash
python3 insert_sensor_data.py
# Choose option 3
```

Expected: SMS with "Critical Fire Risk" alert

---

## 📱 SMS Message Format

### Current + Historical Trend

```
🚨 FIRE ALERT: Critical Fire Risk
CURRENT: Risk:85% Temp:35.0°C Smoke:3200
TREND:
14:30 R:85% S:3200
14:25 R:68% S:2200
14:20 R:55% S:1500
Time: 14:30:45
```

**Benefits:**
- See current critical values at a glance
- Understand the trend (rising/falling)
- Time-stamped for reference

---

## 🔄 How the Monitor Works

1. **Startup**: Monitor starts automatically with backend
2. **Polling Loop**: Every 10 seconds:
   - Fetches latest sensor reading from database
   - Checks if timestamp is newer than last checked
   - Evaluates against thresholds
3. **Alert Trigger**: If thresholds exceeded:
   - Fetches 2-3 recent readings for trend
   - Builds SMS with current + historical data
   - Sends via Twilio
   - Records timestamp to avoid duplicates
4. **Cooldown**: Waits 5-10 minutes before re-alerting

---

## 📈 Integration with External System

### Python Example

```python
import requests
from datetime import datetime

def send_sensor_reading(temp, humidity, smoke, risk_score):
    """Send reading from your external system"""
    
    # Option 1: Direct database insert
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client["forest_fire_db"]
    
    db.sensor_data.insert_one({
        "timestamp": datetime.utcnow(),
        "temperature": temp,
        "humidity": humidity,
        "smoke_level": smoke,
        "rain_level": 0.0,
        "rain_detected": False,
        "fire_risk_score": risk_score,
        "risk_level": "critical" if risk_score >= 75 else "high"
    })
    
    print(f"✅ Sent reading: Risk={risk_score}%, Smoke={smoke}")

# Usage
send_sensor_reading(
    temp=35.0,
    humidity=25.0,
    smoke=3200,
    risk_score=85.0
)
```

### Node.js Example

```javascript
const { MongoClient } = require('mongodb');

async function sendSensorReading(temp, humidity, smoke, riskScore) {
    const client = new MongoClient("mongodb://localhost:27017");
    await client.connect();
    
    const db = client.db("forest_fire_db");
    
    await db.collection("sensor_data").insertOne({
        timestamp: new Date(),
        temperature: temp,
        humidity: humidity,
        smoke_level: smoke,
        rain_level: 0.0,
        rain_detected: false,
        fire_risk_score: riskScore,
        risk_level: riskScore >= 75 ? "critical" : "high"
    });
    
    console.log(`✅ Sent reading: Risk=${riskScore}%, Smoke=${smoke}`);
    await client.close();
}

// Usage
sendSensorReading(35.0, 25.0, 3200, 85.0);
```

---

## 🚨 Troubleshooting

### Monitor Not Running
```bash
# Check status
curl http://localhost:8000/alert-monitor/status

# Check backend logs
# Look for: "🔍 Starting Database Alert Monitor"
```

### SMS Not Sending
1. **Check thresholds exceeded**:
   ```bash
   curl http://localhost:8000/alert-monitor/latest-reading
   ```

2. **Check cooldown period**: Wait 5-10 minutes

3. **Manually trigger**:
   ```bash
   curl -X POST http://localhost:8000/alert-monitor/trigger-check
   ```

4. **Check Twilio credentials** in `.env`

### No Data in Database
```bash
# Insert test data
python3 insert_sensor_data.py

# Or check existing data
python3 test_sms_with_history.py check
```

---

## 📊 Monitoring

### Backend Logs Show:

**Normal operation:**
```
📊 Processing reading from 2025-11-14 14:30:45
   Risk: 45%, Smoke: 800, Temp: 28.0°C
✓ Readings within safe thresholds
```

**Alert triggered:**
```
📊 Processing reading from 2025-11-14 14:30:45
   Risk: 85%, Smoke: 3200, Temp: 35.0°C

⚠️ THRESHOLD EXCEEDED!
   Risk Score: 85% (Threshold: 75%) ✗ EXCEEDED
   Smoke Level: 3200 (Threshold: 2500) ✗ EXCEEDED

🚨 Triggering alert evaluation...
📱 Attempting to send SMS for alert: ALERT-abc123
✅ SMS sent to +917880764235 (SID: SMxxxxx)
```

---

## ✅ Summary

1. **Start backend** → Monitor runs automatically
2. **Insert data** → From your external system into MongoDB
3. **Monitor checks** → Every 10 seconds
4. **SMS sent** → With current + 2-3 historical readings
5. **Repeat** → Continuous monitoring

**No need for real-time streaming!** Just insert data into the database whenever you have new readings, and the system handles the rest.

---

## 🎯 Best Practices

1. **Batch Inserts**: Insert multiple readings at once if you have historical data
2. **Timestamps**: Always use UTC datetime for consistency
3. **Risk Calculation**: Pre-calculate `fire_risk_score` in your system or let the API do it
4. **Testing**: Use `insert_sensor_data.py` to test before integrating
5. **Monitoring**: Check backend logs regularly for alert activity

---

**Last Updated**: November 14, 2025  
**Version**: 3.0.0
