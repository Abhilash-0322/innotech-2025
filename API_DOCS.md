# 📡 API Documentation

Base URL: `http://localhost:8000`

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

**Include JWT token in headers:**
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

---

## 📊 Sensor Data Endpoints

### Get Latest Reading
```http
GET /sensors/latest
Authorization: Bearer <token>
```

**Response:**
```json
{
  "temperature": 28.5,
  "humidity": 45.2,
  "smoke_level": 15,
  "rain_level": 4095.0,
  "rain_detected": false,
  "timestamp": "2025-11-07T10:30:00",
  "fire_risk_score": 35.5,
  "risk_level": "medium"
}
```

### Get Sensor History
```http
GET /sensors/history?hours=24&limit=100
Authorization: Bearer <token>
```

**Query Parameters:**
- `hours` (default: 24) - Time range in hours (1-168)
- `limit` (default: 100) - Maximum number of records (1-1000)

### Get Statistics
```http
GET /sensors/statistics?hours=24
Authorization: Bearer <token>
```

**Response:**
```json
{
  "avg_temperature": 27.8,
  "max_temperature": 32.5,
  "min_temperature": 24.1,
  "avg_humidity": 48.3,
  "max_smoke": 150,
  "avg_smoke": 25.5,
  "total_readings": 1440,
  "period_hours": 24
}
```

---

## 🚨 Alert Endpoints

### Get All Alerts
```http
GET /alerts?status=active&hours=24&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional) - Filter by status: active, acknowledged, resolved
- `hours` (default: 24) - Time range
- `limit` (default: 50) - Max records

### Get Active Alerts
```http
GET /alerts/active
Authorization: Bearer <token>
```

### Acknowledge Alert
```http
PATCH /alerts/{alert_id}/acknowledge
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Alert acknowledged",
  "alert_id": "507f1f77bcf86cd799439011"
}
```

### Resolve Alert
```http
PATCH /alerts/{alert_id}/resolve
Authorization: Bearer <token>
```

### Get Alert Counts
```http
GET /alerts/count
Authorization: Bearer <token>
```

**Response:**
```json
{
  "active": 3,
  "acknowledged": 5,
  "resolved": 12
}
```

---

## 💧 Sprinkler Control Endpoints

### Get Sprinkler Status
```http
GET /sprinkler/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "auto",
  "manual_override": false,
  "timestamp": "2025-11-07T10:30:00",
  "reason": null,
  "activated_at": null
}
```

**Status values:** `on`, `off`, `auto`

### Manual Control
```http
POST /sprinkler/control?action=on&reason=Manual%20test
Authorization: Bearer <token>
```

**Query Parameters:**
- `action` (required) - Action: `on` or `off`
- `reason` (optional) - Reason for action

### Set Auto Mode
```http
POST /sprinkler/auto
Authorization: Bearer <token>
```

### Get Control History
```http
GET /sprinkler/history?limit=50
Authorization: Bearer <token>
```

---

## 📈 Dashboard Endpoints

### Get Dashboard Stats
```http
GET /dashboard/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "current_temperature": 28.5,
  "current_humidity": 45.2,
  "current_smoke": 15,
  "current_risk_level": "medium",
  "current_risk_score": 35.5,
  "active_alerts": 2,
  "sprinkler_status": "auto",
  "total_readings_today": 1440,
  "average_temp_today": 27.8,
  "max_risk_today": 45.0
}
```

### Get Chart Data
```http
GET /dashboard/chart-data?hours=24
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2025-11-07T09:00:00",
      "temperature": 27.5,
      "humidity": 48.0,
      "smoke_level": 10,
      "risk_score": 25.0,
      "risk_level": "low"
    }
  ],
  "period_hours": 24,
  "sample_minutes": 15
}
```

### Get Recent Risk Analysis
```http
GET /dashboard/risk-analysis?limit=10
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "risk_score": 35.5,
    "risk_level": "medium",
    "reasoning": "Elevated temperature and low humidity increase fire risk",
    "recommendations": [
      "Monitor temperature closely",
      "Prepare sprinkler system"
    ],
    "should_activate_sprinkler": false,
    "confidence": 0.92,
    "timestamp": "2025-11-07T10:30:00"
  }
]
```

---

## 🔌 WebSocket Endpoint

### Real-time Updates
```
WS ws://localhost:8000/ws
```

**Messages Received:**
```json
{
  "type": "sensor_update",
  "data": {
    "temperature": 28.5,
    "humidity": 45.2,
    "smoke_level": 15,
    "risk_score": 35.5,
    "risk_level": "medium",
    "timestamp": "2025-11-07T10:30:00"
  }
}
```

**Connection Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
ws.onerror = (error) => console.error('Error:', error);
ws.onclose = () => console.log('Disconnected');
```

---

## 🏥 System Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T10:30:00",
  "database": "connected"
}
```

### Root
```http
GET /
```

**Response:**
```json
{
  "message": "Smart Forest Fire Prevention System API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

## 🔗 Interactive Documentation

Access the auto-generated interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 Error Responses

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Testing with cURL

### Login and Get Token
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=secure_password" \
  | jq -r '.access_token')

# Use token
curl -X GET http://localhost:8000/sensors/latest \
  -H "Authorization: Bearer $TOKEN"
```

### Get Dashboard Stats
```bash
curl -X GET http://localhost:8000/dashboard/stats \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### Control Sprinkler
```bash
curl -X POST "http://localhost:8000/sprinkler/control?action=on&reason=Test" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔒 Security Notes

1. Always use HTTPS in production
2. Keep JWT tokens secure and don't expose them
3. Tokens expire after 30 minutes (configurable)
4. Use strong passwords (minimum 8 characters recommended)
5. Implement rate limiting in production
6. Use environment variables for sensitive data

---

## 📊 Rate Limits (Production)

Recommended rate limits for production:

- Authentication: 5 requests/minute
- Read operations: 100 requests/minute
- Write operations: 20 requests/minute
- WebSocket: 1 connection per user

---

## 🆘 Support

For issues or questions:
- Check `/docs` for interactive documentation
- Review main README.md
- Check system logs for errors
