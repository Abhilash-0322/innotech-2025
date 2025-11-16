# 🔥 SMS Alert Thresholds Configuration Guide

## Overview

The SMS alert system now supports **dual thresholds** for triggering alerts:
1. **Risk Score Threshold** - Based on overall fire risk calculation
2. **Smoke Level Threshold** - Based on direct smoke sensor readings

---

## 📋 Configuration (.env file)

```bash
# SMS Alert Thresholds
SMS_RISK_THRESHOLD=75.0   # Send SMS when fire risk score >= this value (%)
SMS_SMOKE_THRESHOLD=2500  # Send SMS when smoke level >= this value
```

### Recommended Values

| Scenario | Risk Threshold | Smoke Threshold | Description |
|----------|---------------|-----------------|-------------|
| **Conservative** | 85.0 | 3000 | Fewer alerts, only severe cases |
| **Balanced** | 75.0 | 2500 | Good balance (default) |
| **Sensitive** | 60.0 | 2000 | More alerts, early detection |
| **Very Sensitive** | 50.0 | 1500 | Maximum sensitivity |

---

## 🎯 How It Works

### Alert Triggers

**SMS will be sent when ANY of these conditions are met:**

1. **Critical Risk Alert**
   - Condition: `risk_score >= SMS_RISK_THRESHOLD`
   - Priority: CRITICAL
   - Cooldown: 5 minutes
   - Channels: Email, SMS, Push, Siren, Dashboard

2. **Smoke Detection Alert**
   - Condition: `smoke_level >= SMS_SMOKE_THRESHOLD`
   - Priority: HIGH
   - Cooldown: 10 minutes
   - Channels: Email, SMS, Dashboard

---

## 📊 Examples

### Example 1: High Smoke, Low Risk
```
Sensor Data:
- Smoke Level: 3000 ⚠️ (above 2500 threshold)
- Risk Score: 45% (below 75% threshold)

Result: ✅ SMS SENT (Smoke Detection alert triggered)
```

### Example 2: High Risk, Low Smoke
```
Sensor Data:
- Smoke Level: 1500 (below 2500 threshold)
- Risk Score: 80% ⚠️ (above 75% threshold)

Result: ✅ SMS SENT (Critical Risk alert triggered)
```

### Example 3: Both High
```
Sensor Data:
- Smoke Level: 3200 ⚠️ (above 2500 threshold)
- Risk Score: 82% ⚠️ (above 75% threshold)

Result: ✅ 2 SMS SENT (Both alerts triggered)
```

### Example 4: Both Low
```
Sensor Data:
- Smoke Level: 800 (below 2500 threshold)
- Risk Score: 35% (below 75% threshold)

Result: ❌ No SMS (Neither threshold crossed)
```

---

## 🔧 Adjusting Thresholds

### To Make Alerts MORE Sensitive:
```bash
# In .env file
SMS_RISK_THRESHOLD=60.0    # Lower value = more alerts
SMS_SMOKE_THRESHOLD=2000   # Lower value = more alerts
```

### To Make Alerts LESS Sensitive:
```bash
# In .env file
SMS_RISK_THRESHOLD=85.0    # Higher value = fewer alerts
SMS_SMOKE_THRESHOLD=3000   # Higher value = fewer alerts
```

---

## 🧪 Testing Thresholds

### Test Current Configuration:
```bash
cd backend
python test_alert_integration.py
```

This will:
- Show your current thresholds
- Test high smoke scenario
- Test high risk scenario
- Verify SMS sending works

### Test with Specific Values:
```bash
# Edit .env
SMS_SMOKE_THRESHOLD=1000   # Test value

# Restart backend
# Send sensor data with smoke > 1000
# Check if SMS is received
```

---

## 📱 Understanding Smoke Levels

| Smoke Level | Status | Action |
|-------------|--------|--------|
| 0 - 1000 | ✅ Normal | No alert |
| 1000 - 2000 | ⚠️ Elevated | Monitor |
| 2000 - 2500 | 🔶 High | Warning |
| 2500+ | 🚨 Critical | **SMS Alert** |

---

## 🎓 Best Practices

### 1. **Start Conservative**
Begin with higher thresholds and adjust down based on actual conditions:
```bash
SMS_RISK_THRESHOLD=85.0
SMS_SMOKE_THRESHOLD=3000
```

### 2. **Consider Environment**
- **Dry season**: Lower thresholds (more sensitive)
- **Wet season**: Higher thresholds (less sensitive)
- **High-risk areas**: Lower thresholds

### 3. **Monitor False Positives**
If you receive too many false alerts:
```bash
# Increase thresholds gradually
SMS_SMOKE_THRESHOLD=2500  # was 2000
# Test for a week
# Adjust again if needed
```

### 4. **Test Changes**
Always test after changing thresholds:
```bash
python test_alert_integration.py
```

---

## 🔄 Dynamic Adjustment

You can change thresholds without restarting the backend:

1. Edit `.env` file
2. Restart the backend service
3. New thresholds take effect immediately

```bash
# Quick restart
pkill -f "python.*main.py"
python main.py
```

---

## 🚨 Emergency Override

For testing or emergency situations, you can temporarily use very low thresholds:

```bash
# EMERGENCY: Alert on any smoke
SMS_SMOKE_THRESHOLD=100
SMS_RISK_THRESHOLD=10.0
```

**Remember to restore normal values after emergency!**

---

## 📊 Monitoring

Check alert statistics in Twilio Console:
- https://console.twilio.com/us1/monitor/logs/sms

Look for patterns:
- Too many alerts? → Increase thresholds
- Missing important alerts? → Decrease thresholds

---

## ✅ Quick Reference

| Setting | Default | Range | Unit |
|---------|---------|-------|------|
| `SMS_RISK_THRESHOLD` | 75.0 | 0-100 | Percentage |
| `SMS_SMOKE_THRESHOLD` | 2500 | 0-4000+ | Sensor reading |

**Current Configuration** (check with):
```bash
cd backend
python -c "from smart_alerts import alert_system; print(f'Risk: {alert_system.sms_risk_threshold}%, Smoke: {alert_system.sms_smoke_threshold}')"
```

---

## 🎯 Recommended Settings by Location

### Dense Forest Area:
```bash
SMS_RISK_THRESHOLD=70.0
SMS_SMOKE_THRESHOLD=2000
```

### Mixed Vegetation:
```bash
SMS_RISK_THRESHOLD=75.0
SMS_SMOKE_THRESHOLD=2500
```

### Grassland/Dry Area:
```bash
SMS_RISK_THRESHOLD=65.0
SMS_SMOKE_THRESHOLD=1800
```

---

**Last Updated**: November 14, 2025  
**Version**: 2.0.0
