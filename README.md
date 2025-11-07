# 🔥 Smart Forest Fire Prevention System

An AI + IoT-based forest fire prevention system using ESP32, DHT22, and MQ-2 sensors with machine learning-based risk assessment, automatic sprinkler control, and real-time monitoring.

## 🌟 Features

- **Real-time Sensor Monitoring**: ESP32 with DHT22 (temperature/humidity), MQ-2 (smoke), and rain sensors
- **Agentic AI Risk Assessment**: Intelligent fire risk analysis using OpenAI GPT-4
- **Automatic Sprinkler Control**: AI-driven automated fire suppression
- **Real-time Dashboard**: Next.js TypeScript frontend with live data visualization
- **Smart Alerts**: Risk-based alert system with acknowledgment and resolution
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **WebSocket Support**: Real-time updates to connected clients
- **User Authentication**: JWT-based secure access control
- **MongoDB Database**: Persistent storage for sensor data, alerts, and logs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         ESP32 Sensors                        │
│  DHT22 (Temp/Humidity) + MQ-2 (Smoke) + Rain Sensor        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Serial (USB)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Sensor Ingestion Service (Python)               │
│          Reads serial data & sends to FastAPI                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP REST API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  • AI Risk Analysis (Agentic AI)                            │
│  • Alert Management                                          │
│  • Sprinkler Automation                                      │
│  • WebSocket Real-time Updates                              │
│  • JWT Authentication                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                ▼             ▼
        ┌──────────┐   ┌─────────────┐
        │ MongoDB  │   │  Next.js    │
        │ Database │   │  Frontend   │
        └──────────┘   └─────────────┘
```

## 📁 Project Structure

```
INNOTECH-2025/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # MongoDB connection
│   ├── models.py               # Pydantic models
│   ├── auth.py                 # Authentication logic
│   ├── ai_agent.py             # Agentic AI for fire risk
│   ├── sensor_ingestion.py     # Serial data ingestion
│   ├── routes_auth.py          # Auth endpoints
│   ├── routes_sensors.py       # Sensor data endpoints
│   ├── routes_alerts.py        # Alert management
│   ├── routes_sprinkler.py     # Sprinkler control
│   ├── routes_dashboard.py     # Dashboard data
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Home/redirect
│   │   │   ├── login/page.tsx      # Login/Register
│   │   │   ├── dashboard/page.tsx  # Main dashboard
│   │   │   ├── layout.tsx          # Root layout
│   │   │   └── globals.css         # Global styles
│   │   ├── components/
│   │   │   ├── SensorChart.tsx     # Data visualization
│   │   │   ├── AlertsPanel.tsx     # Alert management
│   │   │   └── SprinklerControl.tsx # Sprinkler UI
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── utils.ts            # Utility functions
│   │   └── store/
│   │       └── authStore.ts        # Auth state management
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── port-tester.py          # Original serial port tester
└── sensor_log.txt          # Sensor data logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (local or Atlas)
- ESP32 with sensors connected
- OpenAI API key (optional, for AI features)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

Key environment variables:
```env
MONGODB_URL=mongodb://localhost:27017
SERIAL_PORT=/dev/ttyUSB0  # Change to your ESP32 port
OPENAI_API_KEY=your-api-key-here  # Optional
SECRET_KEY=your-secret-key-change-this
```

5. **Start MongoDB:**
```bash
# If using Docker:
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

6. **Run FastAPI server:**
```bash
python main.py
# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

7. **Run sensor ingestion service (in another terminal):**
```bash
python sensor_ingestion.py
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**
```bash
# .env.local is already created, modify if needed
```

4. **Run development server:**
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 👤 Default User Setup

On first run, register a user through the UI or create one via API:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

## 🎯 Usage

### 1. Access Dashboard
1. Open http://localhost:3000
2. Login or register
3. View real-time sensor data and risk assessment

### 2. Monitor Fire Risk
- Dashboard shows current risk level (LOW, MEDIUM, HIGH, CRITICAL)
- AI analyzes temperature, humidity, smoke levels, and rain data
- Risk score calculated on 0-100 scale

### 3. Manage Alerts
- Active alerts appear in the Alerts Panel
- Acknowledge or resolve alerts
- View alert history

### 4. Control Sprinklers
- **AUTO Mode**: AI automatically activates based on risk
- **Manual ON**: Force activation
- **Manual OFF**: Force deactivation

### 5. View Sensor Trends
- Charts show temperature, humidity, smoke, and risk over time
- Configurable time ranges (6h, 24h, 48h, 1 week)

## 🤖 Agentic AI Features

The system uses OpenAI GPT-4 as an intelligent agent to:

1. **Analyze Sensor Data**: Contextual understanding of environmental conditions
2. **Calculate Risk**: Smart risk scoring based on multiple factors
3. **Make Decisions**: Autonomous sprinkler activation decisions
4. **Provide Reasoning**: Human-readable explanations
5. **Generate Recommendations**: Actionable advice for operators

**Fallback**: Rule-based analysis if AI is unavailable

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Sensors
- `GET /sensors/latest` - Get latest sensor reading
- `GET /sensors/history` - Get sensor history
- `GET /sensors/statistics` - Get statistical summary

### Alerts
- `GET /alerts` - Get all alerts
- `GET /alerts/active` - Get active alerts
- `PATCH /alerts/{id}/acknowledge` - Acknowledge alert
- `PATCH /alerts/{id}/resolve` - Resolve alert

### Sprinkler
- `GET /sprinkler/status` - Get current status
- `POST /sprinkler/control` - Manual control
- `POST /sprinkler/auto` - Set auto mode
- `GET /sprinkler/history` - Get control history

### Dashboard
- `GET /dashboard/stats` - Get comprehensive stats
- `GET /dashboard/chart-data` - Get chart data
- `GET /dashboard/risk-analysis` - Get recent AI analyses

### WebSocket
- `WS /ws` - Real-time updates

## 🔧 Configuration

### Sensor Thresholds
Adjust in `backend/config.py`:
```python
FIRE_RISK_THRESHOLD = 70.0
HIGH_SMOKE_THRESHOLD = 100.0
HIGH_TEMP_THRESHOLD = 35.0
LOW_HUMIDITY_THRESHOLD = 30.0
```

### Serial Port
Change in `.env`:
```env
SERIAL_PORT=/dev/ttyUSB0  # Linux
SERIAL_PORT=/dev/tty.usbserial  # Mac
SERIAL_PORT=COM3  # Windows
```

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Testing API
Use the interactive docs at http://localhost:8000/docs

## 📦 Dependencies

### Backend
- FastAPI - Modern web framework
- Motor - Async MongoDB driver
- PySerial - Serial communication
- OpenAI - AI integration
- Python-Jose - JWT tokens
- Passlib - Password hashing

### Frontend
- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Recharts - Data visualization
- Axios - HTTP client
- Zustand - State management
- Lucide React - Icons

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- Environment variable configuration

## 🐛 Troubleshooting

### Serial Port Issues
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Reboot required

# Check available ports
ls /dev/tty*
```

### MongoDB Connection
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

## 📈 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] SMS/Email notifications
- [ ] Weather API integration
- [ ] Multiple sensor node support
- [ ] Historical data analytics
- [ ] Machine learning model training
- [ ] Drone integration for fire detection
- [ ] Satellite imagery analysis

## 📄 License

This project is for educational and demonstration purposes.

## 👥 Contributors

INNOTECH 2025 Team

## 📞 Support

For issues and questions, please create an issue in the repository.

---

**Built with ❤️ for forest fire prevention**
