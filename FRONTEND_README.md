# 🔥 Smart Forest Fire Prevention System - Frontend

## 🎯 Championship-Grade Web Application

A professional Next.js-based dashboard for real-time forest fire detection and prevention with **advanced AI capabilities**.

---

## ✨ Features Overview

### Core Features (Basic Monitoring)
1. **Live Sensor Data** - Real-time temperature, humidity, smoke detection
2. **Historical Charts** - Trend visualization using Recharts
3. **All Records Viewer** - Searchable sensor data records
4. **AI Responses** - Groq Mixtral-8x7b recommendations
5. **Basic Alerts** - Simple alert notifications
6. **Sprinkler Control** - Manual sprinkler activation

### 🚀 Advanced AI Features (Championship-Winning)
7. **ML Predictions** - Machine Learning fire risk forecasting (24h ahead)
8. **Multi-Zone Heatmap** - 4-zone forest network with fire spread modeling
9. **Advanced Analytics** - Trend analysis, pattern detection, anomaly alerts
10. **Weather & Satellite** - OpenWeatherMap + NASA FIRMS integration
11. **Smart Alerts** - Multi-channel alerts (Email, SMS, Push, Webhook, Voice, Dashboard)
12. **System Health Monitor** - Real-time infrastructure monitoring

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx              # Main dashboard with 12 tabs
│   │   ├── login/
│   │   │   └── page.tsx              # Authentication page
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing page
│   │   └── globals.css                # Global styles
│   │
│   ├── components/                    # React Components
│   │   ├── LiveSensorData.tsx         # Real-time sensor monitoring
│   │   ├── HistoricalData.tsx         # Charts for historical trends
│   │   ├── SensorRecordsViewer.tsx    # All records table
│   │   ├── AIResponsesViewer.tsx      # AI recommendations
│   │   ├── AlertsPanel.tsx            # Basic alerts
│   │   ├── SprinklerControl.tsx       # Sprinkler controls
│   │   ├── AIRecommendationsSidebar.tsx # AI sidebar
│   │   ├── SensorChart.tsx            # Reusable chart component
│   │   │
│   │   # 🚀 Advanced AI Components
│   │   ├── MLPredictions.tsx          # ML fire risk predictions
│   │   ├── MultiZoneHeatmap.tsx       # Multi-zone network visualization
│   │   ├── AdvancedAnalytics.tsx      # Trends, patterns, forecasts
│   │   ├── WeatherSatellite.tsx       # Weather + satellite data
│   │   ├── EnhancedAlertsPanel.tsx    # Smart multi-channel alerts
│   │   └── SystemHealthMonitor.tsx    # System health dashboard
│   │
│   ├── lib/
│   │   ├── api.ts                     # Comprehensive API client
│   │   └── utils.ts                   # Utility functions
│   │
│   └── store/
│       └── authStore.ts               # Zustand auth state management
│
├── public/                            # Static assets
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
├── tailwind.config.js                 # Tailwind CSS config
└── next.config.js                     # Next.js config
```

---

## 🛠️ Technology Stack

### Core Technologies
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Charting Libraries
- **Recharts**: Historical trend charts
- **Chart.js + react-chartjs-2**: ML predictions, analytics

### Date Utilities
- **date-fns**: Date formatting and manipulation

---

## 📊 Dashboard Tabs

| Tab Name | Icon | Description | Category |
|----------|------|-------------|----------|
| **Live Data** | Activity | Real-time sensor monitoring | Core |
| **ML Predictions** | Brain | 24h fire risk forecasting | AI |
| **Multi-Zone** | Map | 4-zone heatmap with fire spread | AI |
| **Analytics** | TrendingUp | Trends, patterns, anomalies | AI |
| **Weather & Satellite** | Satellite | Weather + NASA FIRMS hotspots | AI |
| **Historical Charts** | Database | Trend visualization | Core |
| **All Records** | FileText | Searchable sensor records | Core |
| **AI Responses** | Brain | Groq AI recommendations | Core |
| **Basic Alerts** | AlertTriangle | Simple notifications | Core |
| **Smart Alerts** | Bell | Multi-channel intelligent alerts | AI |
| **Sprinkler** | Droplets | Sprinkler control panel | Control |
| **System Health** | Settings | Infrastructure monitoring | Control |

---

## 🎨 Component Details

### 1. MLPredictions Component
**File**: `src/components/MLPredictions.tsx`

**Features**:
- 24-hour fire risk forecast
- Line chart with Chart.js
- Feature importance visualization
- Model accuracy display (Random Forest + Gradient Boosting)
- Risk score cards

**API Endpoints**:
- `GET /api/predictions/fire-risk`
- `POST /api/predictions/train`
- `GET /api/predictions/feature-importance`

---

### 2. MultiZoneHeatmap Component
**File**: `src/components/MultiZoneHeatmap.tsx`

**Features**:
- Visual heatmap of 4 forest zones
- Real-time risk scores per zone
- Fire spread prediction modeling
- Node status (online/offline)
- Comparison table
- At-risk nodes highlighting

**API Endpoints**:
- `GET /api/zones`
- `GET /api/zones/heatmap`
- `GET /api/zones/{zone_id}/fire-spread`
- `GET /api/zones/comparison`

---

### 3. AdvancedAnalytics Component
**File**: `src/components/AdvancedAnalytics.tsx`

**Features**:
- Linear regression trend analysis
- Pattern detection (temporal, spatial, seasonal, correlation)
- 24-hour risk forecast
- Anomaly detection
- Statistical summaries
- Time range filtering (24h, 7d, 30d, 90d)

**API Endpoints**:
- `GET /api/analytics/trends`
- `GET /api/analytics/patterns`
- `GET /api/analytics/forecast`
- `GET /api/analytics/insights`

---

### 4. WeatherSatellite Component
**File**: `src/components/WeatherSatellite.tsx`

**Features**:
- Current weather from OpenWeatherMap
- 5-day forecast
- NASA FIRMS fire hotspot detection (50km radius)
- Weather-based fire risk assessment
- Temperature, humidity, wind, visibility metrics
- Fire radiative power (FRP) visualization

**API Endpoints**:
- `GET /api/external/weather`
- `GET /api/external/forecast`
- `GET /api/external/fire-hotspots`

---

### 5. EnhancedAlertsPanel Component
**File**: `src/components/EnhancedAlertsPanel.tsx`

**Features**:
- Multi-priority filtering (Critical, High, Medium, Low)
- 6 notification channels: Email, SMS, Push, Webhook, Voice, Dashboard
- Alert acknowledgment
- Alert history tracking
- Channel status monitoring
- Response time analytics
- Automated action logging

**API Endpoints**:
- `GET /api/smart-alerts/active`
- `POST /api/smart-alerts/{alert_id}/acknowledge`
- `GET /api/smart-alerts/statistics`

---

### 6. SystemHealthMonitor Component
**File**: `src/components/SystemHealthMonitor.tsx`

**Features**:
- System health score (0-100%)
- API server status
- Database status
- ML model status
- Performance metrics (CPU, memory, req/sec, error rate)
- Sensor network status
- Battery levels
- Signal strength

**API Endpoints**:
- `GET /api/system/health`

---

## 🔌 API Integration

### API Client (`src/lib/api.ts`)

The API client is organized into modules:

```typescript
// Authentication
authAPI.login(credentials)
authAPI.register(userData)
authAPI.logout()

// Sensors
sensorsAPI.getLive()
sensorsAPI.getHistorical(limit, startDate, endDate)
sensorsAPI.getAllRecords(limit, offset)

// Alerts
alertsAPI.getAll()
alertsAPI.acknowledge(alertId)

// Sprinkler
sprinklerAPI.getStatus()
sprinklerAPI.toggle(nodeId)

// AI
aiAPI.getRecommendations()
aiAPI.analyzeRisk(sensorId)

// Dashboard
dashboardAPI.getStats()

// ML Predictions
mlAPI.getPredictions()
mlAPI.trainModel()
mlAPI.getFeatureImportance()

// Multi-Zone
zoneAPI.getAllZones()
zoneAPI.getHeatmap()
zoneAPI.getFireSpread(zoneId)
zoneAPI.getComparison()

// External Data
externalAPI.getCurrentWeather()
externalAPI.getForecast()
externalAPI.getFireHotspots()

// Analytics
analyticsAPI.getTrends()
analyticsAPI.getPatterns()
analyticsAPI.getForecast()
analyticsAPI.getInsights()

// Smart Alerts
smartAlertsAPI.getActiveAlerts()
smartAlertsAPI.acknowledgeAlert(alertId)
smartAlertsAPI.getStatistics()

// System Health
systemAPI.getHealth()
```

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   ```
   http://localhost:3000
   ```

### Build for Production

```bash
npm run build
npm start
```

---

## 🎯 Environment Configuration

Create `.env.local` (optional):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🎨 UI/UX Highlights

### Design System
- **Color Palette**: 
  - Primary: Orange/Red (fire theme)
  - AI Features: Purple/Indigo badges
  - Status: Green (safe), Yellow (warning), Red (danger)
  
- **Typography**: Inter font (via Tailwind)
  
- **Components**: 
  - Gradient backgrounds for headers
  - Card-based layouts
  - Responsive grid systems
  - Icon-driven navigation
  - Loading states with animations
  - Hover effects and transitions

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Color contrast compliance

---

## 📱 Responsive Design

- **Mobile**: Single column, stacked tabs
- **Tablet**: 2-column grid
- **Desktop**: 3-column layout with sidebar
- **Large Desktop**: Full-width charts and tables

---

## 🔐 Authentication Flow

1. User lands on `/login`
2. JWT token stored in Zustand + localStorage
3. Protected routes redirect to login
4. Token sent in `Authorization: Bearer <token>` header
5. Logout clears auth state

---

## 📈 Performance Optimizations

- **Code Splitting**: Next.js automatic code splitting
- **Lazy Loading**: Dynamic imports for components
- **Auto-refresh**: Smart polling intervals (10s - 5min based on component)
- **Caching**: Axios response caching
- **Optimized Images**: Next.js Image component

---

## 🧪 Testing Recommendations

### Manual Testing
1. Test all 12 dashboard tabs
2. Verify real-time updates
3. Test alert acknowledgment
4. Verify sprinkler control
5. Check responsive design

### Automated Testing (Future)
- Jest + React Testing Library
- Cypress for E2E testing

---

## 🏆 Championship Features Summary

This frontend is designed to **win the INNOTECH-2025 event** with:

✅ **12 Feature-Rich Tabs** (vs competitors' 3-4)  
✅ **AI-Powered Predictions** (ML models for 24h forecasting)  
✅ **Multi-Zone Management** (Fire spread modeling)  
✅ **External Integrations** (Weather + Satellite)  
✅ **Smart Alerts** (6 notification channels)  
✅ **Advanced Analytics** (Pattern detection, anomalies)  
✅ **System Monitoring** (Infrastructure health)  
✅ **Professional UI/UX** (Gradient themes, responsive design)  
✅ **Real-time Updates** (WebSocket + polling)  
✅ **Comprehensive API** (25+ endpoints)

---

## 📝 Dependencies

```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.3",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "tailwindcss": "^3.3.6",
    "lucide-react": "^0.294.0",
    "date-fns": "^3.0.0",
    "zustand": "^4.4.7"
  }
}
```

---

## 🤝 Team & Credits

**Developed for**: INNOTECH-2025 Competition  
**Stack**: Next.js + TypeScript + Tailwind CSS  
**AI Integration**: Groq Mixtral-8x7b, Scikit-learn ML models  
**External APIs**: OpenWeatherMap, NASA FIRMS

---

## 📞 Support

For issues or questions:
1. Check backend API logs
2. Verify network requests in browser DevTools
3. Check console for errors
4. Ensure all dependencies are installed

---

## 🎉 Winning Strategy

**Why This Frontend Will Win:**

1. **Feature Density**: 12 tabs vs competitors' basic dashboards
2. **AI Integration**: Multiple ML models, not just threshold alerts
3. **External Data**: Weather + satellite integration
4. **Professional Design**: Gradient themes, responsive, modern UI
5. **Real-world Ready**: Multi-channel alerts, system monitoring
6. **Scalable Architecture**: Clean component structure, TypeScript
7. **Documentation**: Comprehensive README, inline comments

**Demo Flow**:
1. Show Live Data → Basic monitoring
2. Switch to ML Predictions → 24h forecasting
3. Demo Multi-Zone → Fire spread simulation
4. Show Weather & Satellite → NASA FIRMS hotspots
5. Display Smart Alerts → 6-channel notifications
6. End with System Health → Professional monitoring

---

**🏆 This is a championship-grade web application designed to outperform all competition!**
