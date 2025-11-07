# 🚀 Quick Start Guide

## Fastest Setup (5 minutes)

### 1. Prerequisites Check
```bash
# Check Python version (needs 3.9+)
python3 --version

# Check Node.js version (needs 18+)
node --version

# Check MongoDB (install if needed)
mongosh --version
```

### 2. Clone or Navigate to Project
```bash
cd /home/abhilash/codespace/INNOTECH-2025
```

### 3. Quick Setup (Run Script)
```bash
chmod +x setup.sh
./setup.sh
```

### 4. Configure Backend
```bash
cd backend
nano .env  # or use your preferred editor
```

**Minimum required configuration:**
```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=change-this-to-a-secure-random-string
SERIAL_PORT=/dev/ttyUSB0  # Your ESP32 port
```

**Optional (for AI features):**
```env
OPENAI_API_KEY=sk-your-openai-key-here
```

### 5. Start All Services

**Option A: Manual (Recommended for Development)**

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python main.py
```

Terminal 2 - Sensor Service:
```bash
cd backend
source venv/bin/activate
python sensor_ingestion.py
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

**Option B: Automated**
```bash
chmod +x start.sh
./start.sh
```

### 6. Access the Application

1. Open browser: http://localhost:3000
2. Register a new account
3. Login and view dashboard
4. API docs: http://localhost:8000/docs

## 📝 First Use Checklist

- [ ] MongoDB is running
- [ ] Backend API is accessible (http://localhost:8000/health)
- [ ] ESP32 is connected and sending data
- [ ] Frontend loads without errors
- [ ] Can register and login
- [ ] Dashboard displays sensor data
- [ ] Alerts are being generated
- [ ] Sprinkler controls work

## 🔍 Verify Installation

```bash
# Test backend
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","database":"connected"}
```

## 🐛 Common Issues

### Issue: MongoDB not running
```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or start local MongoDB service
sudo systemctl start mongod
```

### Issue: Serial port permission denied
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again

# Or use sudo (not recommended)
sudo python sensor_ingestion.py
```

### Issue: Frontend won't start
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Issue: Port already in use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
sudo lsof -ti:3000 | xargs kill -9
```

## 🎯 Test the System

1. **Register User:**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Fill in details

2. **View Dashboard:**
   - Login with credentials
   - Observe real-time data

3. **Test Sprinkler Control:**
   - Click "Turn ON" in Sprinkler Control panel
   - Verify status changes

4. **Generate Alert:**
   - If smoke sensor detects high values, alert will appear
   - Acknowledge or resolve from Alerts panel

## 📚 Next Steps

- Configure sensor thresholds in `backend/config.py`
- Set up OpenAI API for enhanced AI features
- Customize frontend styling
- Set up email/SMS notifications
- Deploy to production

## 💡 Tips

- Keep MongoDB running in background
- Monitor backend logs for errors
- Use API docs for testing endpoints
- Check browser console for frontend errors
- Sensor data refreshes every 10 seconds

## 🆘 Need Help?

Check the main README.md for detailed documentation or create an issue.
