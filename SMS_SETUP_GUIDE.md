# 📱 SMS Alert System - Setup & Usage Guide

## Overview
The SMS Alert System automatically sends text messages to configured phone numbers when fire risk levels exceed a threshold. This feature uses **Twilio** for reliable SMS delivery.

---

## 🚀 Quick Setup

### Step 1: Get Twilio Credentials

1. **Sign up for Twilio** (Free trial available):
   - Go to: https://www.twilio.com/try-twilio
   - Sign up and verify your account
   - Get **$15 free trial credit** (enough for ~500 SMS messages)

2. **Get your credentials**:
   - **Account SID**: Found on your Twilio Console Dashboard
   - **Auth Token**: Found on your Twilio Console Dashboard (click "show" to reveal)
   - **Phone Number**: Get a free phone number from Twilio Console

3. **For Trial Accounts**:
   - You can only send SMS to **verified phone numbers**
   - Add recipient numbers in: Console → Phone Numbers → Verified Caller IDs

---

### Step 2: Configure Environment Variables

Create or update `.env` file in the `backend/` directory:

```bash
# SMS/Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number

# SMS Recipients (comma-separated, with country codes)
SMS_RECIPIENTS=+919876543210,+911234567890,+14155552671

# SMS Alert Threshold (send SMS when risk >= this value)
SMS_RISK_THRESHOLD=75.0

# Email Configuration (optional, for email alerts)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENTS=admin@example.com,team@example.com
```

**Important Phone Number Format**:
- ✅ Correct: `+919876543210` (with country code)
- ❌ Wrong: `9876543210` (missing country code)
- ❌ Wrong: `+91 9876 543 210` (no spaces or dashes)

---

### Step 3: Install Twilio Library

```bash
cd backend
pip install twilio
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

---

## 📋 API Endpoints

All endpoints require authentication (JWT token in Authorization header).

### 1. Get SMS Status
```http
GET /sms/status
```

**Response**:
```json
{
  "configured": true,
  "twilio_configured": true,
  "recipients_count": 2,
  "recipients": ["+919876543210", "+911234567890"],
  "last_sms_sent": "Never"
}
```

---

### 2. Send Test SMS
```http
POST /sms/test
Content-Type: application/json

{
  "phone_number": "+919876543210",
  "message": "Test alert from Forest Fire System"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Test SMS sent successfully",
  "sid": "SM1234567890abcdef",
  "to": "+919876543210",
  "status": "queued"
}
```

---

### 3. Send Test Alert SMS
```http
POST /sms/test-alert
```

Sends a realistic fire alert SMS to all configured recipients.

**Response**:
```json
{
  "success": true,
  "message": "Test alert SMS sent to 2 recipient(s)",
  "recipients": ["+919876543210", "+911234567890"],
  "alert_id": "TEST-a1b2c3d4"
}
```

---

### 4. Get Recipients List
```http
GET /sms/recipients
```

**Response**:
```json
{
  "recipients": ["+919876543210", "+911234567890"],
  "count": 2
}
```

---

### 5. Add Recipient
```http
POST /sms/recipients/add?phone_number=+919998887777
```

**Response**:
```json
{
  "message": "Recipient added successfully",
  "phone_number": "+919998887777",
  "total_recipients": 3
}
```

---

### 6. Remove Recipient
```http
DELETE /sms/recipients/+919998887777
```

**Response**:
```json
{
  "message": "Recipient removed successfully",
  "phone_number": "+919998887777",
  "remaining_recipients": 2
}
```

---

### 7. Update SMS Configuration
```http
POST /sms/config
Content-Type: application/json

{
  "recipients": ["+919876543210", "+911234567890"],
  "enabled": true
}
```

---

## 🔥 How Automatic SMS Alerts Work

### Trigger Conditions

SMS alerts are automatically sent when any of these conditions are met:

1. **Critical Fire Risk** (Risk Score ≥ 75%)
   - Channels: Email, SMS, Push, Siren, Dashboard
   - Cooldown: 5 minutes

2. **High Smoke Detection** (Smoke Level > 2500)
   - Channels: Email, SMS, Dashboard
   - Cooldown: 10 minutes

3. **Sprinkler Activation**
   - Channels: Email, SMS, Dashboard
   - Cooldown: None (always alert)

4. **Nearby Fire Hotspot** (< 10km away)
   - Channels: Email, SMS, Push, Dashboard
   - Cooldown: 60 minutes

### SMS Message Format

```
🚨 FIRE ALERT: Critical Fire Risk
Risk: 82% | Temp: 38.5°C | Smoke: 2800
Time: 14:23:45
ID: ALERT-a1b2c3d4
```

- Maximum 160 characters for compatibility
- Includes emoji indicator based on priority:
  - ℹ️ Low
  - ⚠️ Medium
  - 🔥 High
  - 🚨 Critical

---

## 🧪 Testing the System

### Test 1: Configuration Check
```bash
curl -X GET "http://localhost:8000/sms/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test 2: Send Test Message
```bash
curl -X POST "http://localhost:8000/sms/test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "message": "Test from Forest Fire System"
  }'
```

### Test 3: Send Test Alert
```bash
curl -X POST "http://localhost:8000/sms/test-alert" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 💰 Cost Estimation

### Twilio Pricing (as of 2024)
- **India**: ~$0.0085 per SMS (~₹0.70)
- **USA**: ~$0.0079 per SMS
- **Free Trial**: $15 credit = ~500-600 SMS messages

### Example Monthly Costs

**Low Activity** (10 alerts/month):
- 10 alerts × 2 recipients = 20 SMS
- Cost: ~$0.17/month (~₹14/month)

**Medium Activity** (50 alerts/month):
- 50 alerts × 2 recipients = 100 SMS
- Cost: ~$0.85/month (~₹70/month)

**High Activity** (200 alerts/month):
- 200 alerts × 5 recipients = 1000 SMS
- Cost: ~$8.50/month (~₹700/month)

---

## 🔒 Security Best Practices

1. **Never commit credentials to git**:
   ```bash
   # Add to .gitignore
   .env
   *.env
   ```

2. **Use environment variables**:
   ```bash
   export TWILIO_ACCOUNT_SID="your_sid"
   export TWILIO_AUTH_TOKEN="your_token"
   ```

3. **Rotate credentials regularly**:
   - Change auth token every 3-6 months
   - Use Twilio's API key authentication for production

4. **Limit recipient list**:
   - Only add trusted personnel
   - Keep list updated (remove inactive numbers)

---

## 🐛 Troubleshooting

### Error: "SMS not configured"
**Solution**: Verify environment variables are set:
```bash
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN
echo $TWILIO_PHONE_NUMBER
```

### Error: "Phone number must start with country code"
**Solution**: Add `+` and country code:
- India: `+91`
- USA: `+1`
- UK: `+44`

### Error: "Twilio library not installed"
**Solution**:
```bash
pip install twilio
```

### SMS not received
**Possible causes**:
1. **Trial account**: Recipient number not verified in Twilio Console
2. **Invalid number**: Check number format (must include `+` and country code)
3. **No credit**: Check Twilio account balance
4. **Network delay**: SMS can take 5-30 seconds to deliver

---

## 📊 Monitoring

### Check SMS Delivery in Twilio Console
1. Go to: https://console.twilio.com/
2. Navigate to: Messaging → Logs → Message Logs
3. View delivery status for each SMS:
   - ✅ Delivered
   - ⏳ Queued/Sent
   - ❌ Failed/Undelivered

### Backend Logs
```bash
# Watch backend logs for SMS activity
tail -f backend.log

# Look for:
✅ SMS sent to +919876543210 (SID: SM123...)
❌ Failed to send SMS to +911234567890: Invalid number
📱 SMS Alert Summary: 2 sent, 0 failed
```

---

## 🌍 Supported Countries

Twilio supports SMS in 200+ countries. Popular destinations:
- 🇮🇳 India: +91
- 🇺🇸 USA: +1
- 🇬🇧 UK: +44
- 🇨🇦 Canada: +1
- 🇦🇺 Australia: +61
- 🇩🇪 Germany: +49
- 🇫🇷 France: +33

Check full list: https://www.twilio.com/docs/sms/pricing

---

## 🔄 Alternative SMS Providers

If you prefer not to use Twilio, you can integrate:

1. **AWS SNS** (Amazon Simple Notification Service)
2. **Vonage (Nexmo)**
3. **MessageBird**
4. **Plivo**

The code in `smart_alerts.py` can be modified to support any provider.

---

## 📞 Support

### Need Help?
1. Check Twilio documentation: https://www.twilio.com/docs/sms
2. Review backend logs for error messages
3. Test with `/sms/test` endpoint first
4. Verify phone number format (must include country code)

### Emergency Contact
For critical production issues:
- Twilio Support: https://support.twilio.com/
- Check Twilio Status: https://status.twilio.com/

---

## ✅ Quick Checklist

Before going live, ensure:
- [ ] Twilio account created and verified
- [ ] Environment variables configured in `.env`
- [ ] Twilio library installed (`pip install twilio`)
- [ ] Test SMS sent successfully (`/sms/test`)
- [ ] Recipient numbers verified (if using trial account)
- [ ] SMS threshold configured (`SMS_RISK_THRESHOLD`)
- [ ] Phone numbers include country codes (start with `+`)
- [ ] Alert rules enabled in `smart_alerts.py`
- [ ] Sufficient Twilio credit balance

---

## 🎯 Example Use Cases

### Use Case 1: Single Administrator
```bash
# .env
SMS_RECIPIENTS=+919876543210
SMS_RISK_THRESHOLD=75.0
```
Perfect for personal projects or small deployments.

### Use Case 2: Team Notifications
```bash
# .env
SMS_RECIPIENTS=+919876543210,+911234567890,+918765432109
SMS_RISK_THRESHOLD=70.0
```
Notify multiple team members (forest rangers, fire department, etc.).

### Use Case 3: Escalation Chain
Configure different thresholds:
- Risk ≥ 60%: Dashboard only
- Risk ≥ 70%: Email + Dashboard
- Risk ≥ 80%: SMS + Email + Dashboard + Siren

---

## 🚀 Production Deployment

### Recommended Configuration

```bash
# Production .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_production_auth_token_here
TWILIO_PHONE_NUMBER=+19876543210

# Multiple recipients with roles
SMS_RECIPIENTS=+919876543210,+911234567890,+918765432109

# Conservative threshold to avoid spam
SMS_RISK_THRESHOLD=75.0

# Email for less urgent alerts
EMAIL_RECIPIENTS=team@company.com,backup@company.com
```

### Monitoring Setup
1. Enable Twilio webhook notifications
2. Set up alerting for failed SMS
3. Monitor Twilio account balance
4. Review SMS logs weekly

---

**Last Updated**: November 13, 2025  
**Version**: 1.0.0  
**Powered by**: Twilio SMS API
