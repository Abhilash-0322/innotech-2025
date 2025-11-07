# 🎯 Next Steps - Getting Your System Running

## Immediate Actions (Required)

### 1. Install MongoDB (if not already installed)

**Option A: Docker (Recommended)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option B: Local Installation**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb-org

# macOS
brew install mongodb-community
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env  # Edit with your settings
```

**Minimum .env configuration:**
```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-random-secret-key-here
SERIAL_PORT=/dev/ttyUSB0  # Your ESP32 port
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# No configuration needed, .env.local is already set
```

### 4. Start the System

Open **3 separate terminals**:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate
python main.py
```
Wait for: "✅ Connected to MongoDB"

**Terminal 2 - Sensor Service:**
```bash
cd backend
source venv/bin/activate
python sensor_ingestion.py
```
Wait for: "✅ Connected! Listening for sensor data..."

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```
Wait for: "Ready on http://localhost:3000"

### 5. Access the System

1. Open browser: **http://localhost:3000**
2. Click "Sign Up" to create account
3. Login with your credentials
4. View the dashboard!

---

## Optional Enhancements

### Enable AI Features (OpenAI)

1. Get API key from: https://platform.openai.com/api-keys
2. Edit `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart backend service

### Configure Sensor Thresholds

Edit `backend/config.py`:
```python
FIRE_RISK_THRESHOLD = 70.0
HIGH_SMOKE_THRESHOLD = 100.0
HIGH_TEMP_THRESHOLD = 35.0
LOW_HUMIDITY_THRESHOLD = 30.0
```

### Setup Email Alerts (Future Enhancement)

Add to `backend/.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Troubleshooting

### MongoDB Not Connecting
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# If not, start it:
docker start mongodb
# or
sudo systemctl start mongod
```

### Serial Port Permission Denied
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then logout and login again
```

### Port Already in Use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
sudo lsof -ti:3000 | xargs kill -9
```

### Frontend Won't Build
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend Import Errors
```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## Testing Your Setup

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy",...}`

### 2. Test API Docs
Open: http://localhost:8000/docs
You should see interactive API documentation

### 3. Test Frontend
Open: http://localhost:3000
You should see the login page

### 4. Register User
Click "Sign Up" and create an account

### 5. View Dashboard
After login, you should see the dashboard with real-time data

---

## Monitoring Your System

### Backend Logs
The terminal running `python main.py` will show:
- Incoming requests
- AI analysis results
- Alert generation
- Sprinkler control actions

### Sensor Service Logs
The terminal running `sensor_ingestion.py` will show:
- Sensor readings
- Risk assessments
- Automation decisions

### Frontend Console
Open browser DevTools (F12) to see:
- API calls
- WebSocket connections
- State updates

---

## Development Tips

### Hot Reload
- Backend: Changes auto-reload (if using `--reload`)
- Frontend: Changes auto-reload automatically

### Testing API Endpoints
Use the interactive docs at `/docs`:
1. Click "Authorize" button
2. Login to get token
3. Test any endpoint

### Viewing Database
```bash
# Connect to MongoDB
mongosh

# Switch to database
use forest_fire_system

# View collections
show collections

# Query data
db.sensor_data.find().limit(5)
db.alerts.find({status: "active"})
```

---

## Production Deployment (Future)

### 1. Update Environment Variables
```env
# Use production URLs
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
FRONTEND_URL=https://yourdomain.com
SECRET_KEY=very-long-random-production-key
```

### 2. Build Frontend
```bash
cd frontend
npm run build
npm start
```

### 3. Use Process Manager
```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start backend/main.py --name fire-backend

# Start frontend
pm2 start npm --name fire-frontend -- start
```

### 4. Setup Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://localhost:8000;
    }

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

### 5. SSL Certificate
```bash
# Using certbot
sudo certbot --nginx -d yourdomain.com
```

---

## Support & Resources

### Documentation
- **README.md** - Complete system documentation
- **QUICKSTART.md** - Quick start guide
- **API_DOCS.md** - API reference
- **ARCHITECTURE.md** - System design

### Online Resources
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs
- MongoDB Docs: https://docs.mongodb.com
- OpenAI Docs: https://platform.openai.com/docs

### Getting Help
1. Check documentation files
2. Review API docs at `/docs`
3. Check console logs for errors
4. Verify all services are running

---

## Success Checklist

- [ ] MongoDB installed and running
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] All three services running
- [ ] Can access http://localhost:3000
- [ ] Can register and login
- [ ] Dashboard displays data
- [ ] API docs accessible at /docs

---

## 🎉 Ready to Go!

Once all services are running and you can access the dashboard, you're all set!

The system will:
- ✅ Read sensor data from ESP32
- ✅ Analyze fire risk with AI
- ✅ Generate alerts automatically
- ✅ Control sprinklers intelligently
- ✅ Display real-time dashboard
- ✅ Store all data in MongoDB

**Happy fire prevention! 🔥🚒💧**
