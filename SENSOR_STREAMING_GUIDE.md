# 🔴 LIVE SENSOR STREAMING GUIDE

## Quick Start

### 1. Start the Backend API (if not already running)
```bash
cd backend
python3 main.py
# or
uvicorn main:app --reload
```

### 2. Start the Frontend (if not already running)
```bash
cd frontend
npm run dev
```

### 3. Start the Sensor Stream
```bash
# Option 1: Use the quick start script
./start_sensor_stream.sh

# Option 2: Run directly
cd backend
python3 start_sensor_stream.py
```

## What Happens?

When you start the sensor stream:

1. **📡 Reads ESP32 Data**: Connects to `/dev/ttyUSB0` (or your configured serial port)
2. **🤖 AI Analysis**: Each reading is analyzed for fire risk using Groq AI
3. **💾 Stores in MongoDB**: Saves sensor data and risk assessments to database
4. **📢 Broadcasts Live**: Sends data to all connected dashboard clients via WebSocket
5. **🖥️ Updates Dashboard**: Your frontend "Live Data" tab updates in real-time!

## Dashboard Features

### Tab 1: Live Data ✅
- **Real-time sensor readings** (temperature, humidity, smoke, rain)
- **Live fire risk assessment** with AI recommendations
- **Recent readings table** (last 20 readings)
- **WebSocket status** indicator
- Updates automatically as new data arrives!

### Tab 2: Historical Data 📊
- Interactive charts with time range selection
- 6h, 24h, 48h, 1 week views
- Trend analysis
- Risk score over time

### Tab 3: Alerts 🚨
- Active fire alerts
- Alert history
- Severity filtering
- Quick actions

### Tab 4: Sprinkler Control 💧
- Manual control (Activate/Deactivate)
- Automatic mode
- Status monitoring
- Control history

## Expected Console Output

When streaming starts, you'll see:

```
🚀 Starting Sensor Data Stream...
📡 Port: /dev/ttyUSB0
⚡ Baud Rate: 115200
✅ Serial connection established

🔴 LIVE STREAMING - Press Ctrl+C to stop

============================================================

📊 Live Sensor Data:
   🌡️  Temp: 28.5°C
   💧 Humidity: 65.2%
   💨 Smoke: 150
   🌧️  Rain: No
   🔥 Risk: MEDIUM (45/100)
```

## Troubleshooting

### No data appearing on dashboard?

1. **Check WebSocket connection**:
   - Open browser console (F12)
   - Look for "✅ WebSocket connected" message
   - If not, ensure backend is running

2. **Check sensor stream**:
   - Terminal should show "Live Sensor Data" updates
   - If not, check ESP32 connection

3. **Check serial port**:
   ```bash
   ls /dev/ttyUSB*
   # or
   ls /dev/ttyACM*
   ```
   
   Update `backend/.env` if needed:
   ```env
   SERIAL_PORT=/dev/ttyUSB0  # or your correct port
   ```

### Permission denied on serial port?

```bash
sudo chmod 666 /dev/ttyUSB0
# or add your user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login again
```

### WebSocket disconnects?

- Check if backend is still running
- Look for error messages in backend terminal
- Refresh the browser page

## System Architecture

```
ESP32 Sensors
     ↓ (Serial)
start_sensor_stream.py
     ↓
  ┌──────────────┐
  │ Parse Data   │
  │ AI Analysis  │
  │ Store in DB  │
  └──────────────┘
     ↓ (HTTP POST)
FastAPI /api/broadcast
     ↓ (WebSocket)
Connected Browsers
     ↓
Dashboard Updates!
```

## Next Steps

1. ✅ Login to dashboard (http://localhost:3000)
2. ✅ Start sensor stream
3. ✅ Watch live data on "Live Data" tab
4. ✅ View trends on "Historical Data" tab
5. ✅ Monitor alerts on "Alerts" tab
6. ✅ Control sprinklers on "Sprinkler Control" tab

## Adding More Features Later

You can easily extend this system:

- 📧 Email/SMS notifications
- 📱 Mobile app integration
- 🗺️ Multiple location monitoring
- 📈 Advanced analytics
- 🎯 Custom alert rules
- 🌐 Public API endpoints
- 📷 Camera integration
- ☁️ Cloud deployment

**Enjoy your Smart Forest Fire Prevention System! 🔥🚒💧**
