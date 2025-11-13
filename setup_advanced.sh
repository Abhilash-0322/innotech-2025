#!/bin/bash

# 🚀 QUICK SETUP SCRIPT FOR INNOTECH 2025
# Run this to set up everything automatically

echo "=============================================="
echo "🔥 Smart Forest Fire Prevention System Setup"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠️  npm not found. Frontend setup will be skipped.${NC}"
fi

# Backend setup
echo -e "\n${GREEN}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create models directory
echo "Creating models directory..."
mkdir -p models

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=forest_fire_db

# JWT Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# OpenWeatherMap API Configuration (Optional)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Serial Port Configuration
SERIAL_PORT=/dev/ttyUSB0
BAUD_RATE=115200

# Fire Risk Thresholds
HIGH_TEMP_THRESHOLD=35
LOW_HUMIDITY_THRESHOLD=30
HIGH_SMOKE_THRESHOLD=2000

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF
    echo -e "${YELLOW}⚠️  .env file created. Please update API keys!${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

cd ..

# Frontend setup
if command -v npm &> /dev/null; then
    echo -e "\n${GREEN}📦 Setting up Frontend...${NC}"
    cd frontend
    
    echo "Installing npm dependencies..."
    npm install
    
    cd ..
else
    echo -e "${YELLOW}⚠️  Skipping frontend setup (npm not found)${NC}"
fi

# Check if MongoDB is running
echo -e "\n${GREEN}🔍 Checking MongoDB...${NC}"
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${YELLOW}⚠️  MongoDB not running. Please start MongoDB:${NC}"
    echo "   sudo systemctl start mongod"
else
    echo -e "${GREEN}✅ MongoDB is running${NC}"
fi

# Create startup scripts
echo -e "\n${GREEN}📝 Creating startup scripts...${NC}"

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "🚀 Starting Backend Server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x start_backend.sh

# Frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "🚀 Starting Frontend Server..."
npm run dev
EOF
chmod +x start_frontend.sh

# Sensor ingestion script
cat > start_sensor_ingestion.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "📡 Starting Sensor Data Ingestion..."
python sensor_ingestion.py
EOF
chmod +x start_sensor_ingestion.sh

# Demo script
cat > run_demo.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "🎮 Running Advanced Features Demo..."
python demo_advanced_features.py
EOF
chmod +x run_demo.sh

echo -e "\n${GREEN}=============================================="
echo "✅ Setup Complete!"
echo "==============================================${NC}"

echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo ""
echo "1. Update API Keys in backend/.env:"
echo "   • GROQ_API_KEY (Get from: https://console.groq.com)"
echo "   • OPENWEATHER_API_KEY (Optional, from: https://openweathermap.org/api)"
echo ""
echo "2. Start MongoDB (if not running):"
echo "   sudo systemctl start mongod"
echo ""
echo "3. Create Admin User:"
echo "   • Start backend: ./start_backend.sh"
echo "   • Go to http://localhost:8000/docs"
echo "   • Use POST /api/auth/register to create admin user"
echo ""
echo "4. Start the application:"
echo "   Terminal 1: ./start_backend.sh"
echo "   Terminal 2: ./start_frontend.sh"
echo "   Terminal 3: ./start_sensor_ingestion.sh (if ESP32 connected)"
echo ""
echo "5. Run the demo:"
echo "   ./run_demo.sh"
echo ""
echo "6. Access the application:"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Frontend: http://localhost:3000"
echo "   • Dashboard: http://localhost:3000/dashboard"
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "   • README.md - Project overview"
echo "   • CHAMPIONSHIP_README.md - Competition guide"
echo "   • ADVANCED_FEATURES.md - Feature documentation"
echo "   • ARCHITECTURE.md - System architecture"
echo ""
echo -e "${GREEN}🎯 For the Competition:${NC}"
echo "   1. Review CHAMPIONSHIP_README.md for presentation strategy"
echo "   2. Test demo_advanced_features.py to ensure all features work"
echo "   3. Train ML model: POST /api/ml/train (after collecting data)"
echo "   4. Configure email alerts in backend/smart_alerts.py"
echo ""
echo -e "${GREEN}Good luck with INNOTECH 2025! 🏆${NC}"
echo ""
