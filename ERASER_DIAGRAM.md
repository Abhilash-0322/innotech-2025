# Smart Forest Fire Prevention System - Eraser.io Diagram

## System Architecture (Eraser Syntax)

```eraser
title Smart Forest Fire Prevention System - Complete Architecture

// ============ HARDWARE LAYER ============
cloud Hardware [icon: cpu] {
  ESP32 [icon: microchip, color: red] {
    description: WiFi/BLE Microcontroller
  }
  
  DHT22 [icon: thermometer, color: orange] {
    description: Temperature & Humidity Sensor
  }
  
  MQ2 [icon: activity, color: yellow] {
    description: Smoke/Gas Sensor
  }
  
  RainSensor [icon: cloud-drizzle, color: blue] {
    description: Rain Detection Sensor
  }
}

// ============ BACKEND LAYER ============
cloud Backend [icon: server, color: blue] {
  
  // Data Ingestion
  group DataIngestion [color: orange] {
    SerialPort [icon: usb] {
      description: /dev/ttyUSB0 - 115200 baud
    }
    
    SensorIngestion [icon: download] {
      description: sensor_ingestion.py
      responsibility: Parse & validate sensor data
    }
    
    WebSocketManager [icon: radio] {
      description: Real-time broadcast to clients
    }
  }
  
  // Core Services
  group CoreServices [color: blue] {
    FastAPI [icon: zap] {
      description: Main API Server - Port 8000
    }
    
    AuthService [icon: shield] {
      description: auth.py - JWT authentication
    }
    
    DatabaseManager [icon: database] {
      description: database.py - Motor AsyncIO
    }
  }
  
  // API Routes
  group APIRoutes [color: cyan] {
    AuthRoutes [icon: key] {
      description: /auth/* - Login, Register
    }
    
    SensorRoutes [icon: activity] {
      description: /sensors/* - Latest, History
    }
    
    DashboardRoutes [icon: layout] {
      description: /dashboard/* - Stats, Charts
    }
    
    AlertRoutes [icon: bell] {
      description: /alerts/* - Alert Management
    }
    
    SprinklerRoutes [icon: droplet] {
      description: /sprinkler/* - Control System
    }
    
    MLRoutes [icon: cpu] {
      description: /api/predictions/* - ML Predictions
    }
    
    WeatherRoutes [icon: cloud] {
      description: /api/weather/* - External Weather
    }
    
    ZoneRoutes [icon: map] {
      description: /api/zones/* - Multi-Zone
    }
    
    AnalyticsRoutes [icon: bar-chart] {
      description: /api/analytics/* - Insights
    }
  }
  
  // Intelligence Layer
  group Intelligence [color: green] {
    MLPredictor [icon: cpu] {
      description: ml_predictor.py
      responsibility: Fire risk prediction using Random Forest & Gradient Boosting
      features: 13 features including temp, humidity, smoke, temporal patterns
    }
    
    AIAgent [icon: brain] {
      description: ai_agent.py
      responsibility: AI-powered risk analysis using Groq Llama 3.1
    }
    
    ExternalIntegrator [icon: globe] {
      description: external_integrator.py
      responsibility: Weather & satellite data integration
      apis: OpenWeatherMap, NASA FIRMS
    }
    
    AnalyticsEngine [icon: trending-up] {
      description: analytics_engine.py
      responsibility: Pattern detection, trend analysis, forecasting
    }
    
    AlertSystem [icon: alert-triangle] {
      description: smart_alerts.py
      responsibility: Priority-based alert generation
      priorities: low, medium, high, critical
    }
    
    MultiZoneManager [icon: layers] {
      description: multi_zone_manager.py
      responsibility: Multi-zone forest monitoring
    }
    
    SprinklerControl [icon: droplet] {
      description: Auto & manual sprinkler activation
    }
  }
}

// ============ DATABASE ============
cloud Database [icon: database, color: purple] {
  MongoDB [icon: database] {
    description: MongoDB Atlas - Cloud Database
  }
  
  group Collections {
    SensorData {
      fields: temperature, humidity, smoke_level, rain_level, timestamp, risk_score
    }
    
    Users {
      fields: email, password_hash, role, full_name, is_active
    }
    
    Alerts {
      fields: title, message, severity, status, timestamp
    }
    
    SprinklerLogs {
      fields: action, triggered_by, reason, duration, timestamp
    }
    
    Predictions {
      fields: risk_score, risk_level, confidence, hours_ahead
    }
    
    WeatherCache {
      fields: temperature, humidity, wind_speed, description, location
    }
  }
}

// ============ FRONTEND ============
cloud Frontend [icon: monitor, color: purple] {
  
  NextJS [icon: layout] {
    description: Next.js 14 App Router - Port 3000
  }
  
  group Pages {
    LoginPage [icon: log-in] {
      route: /login
    }
    
    DashboardPage [icon: layout] {
      route: /dashboard
    }
  }
  
  group Components [color: pink] {
    LiveSensorData [icon: activity] {
      description: Real-time sensor display with WebSocket
    }
    
    SensorChart [icon: bar-chart] {
      description: Recharts visualization
    }
    
    HistoricalData [icon: clock] {
      description: Data table with pagination
    }
    
    AlertsPanel [icon: bell] {
      description: Alert management UI
    }
    
    SprinklerControlUI [icon: droplet] {
      description: Manual sprinkler control
    }
    
    AIRecommendations [icon: message-square] {
      description: AI-powered insights sidebar
    }
    
    WeatherSatellite [icon: cloud] {
      description: Weather & fire hotspots for Delhi
      features: IST timezone, location display, forecast
    }
    
    AnalyticsCharts [icon: trending-up] {
      description: Trends, patterns, insights
    }
  }
  
  group StateManagement {
    AuthStore [icon: box] {
      description: Zustand store for authentication
    }
    
    LocalStorage [icon: save] {
      description: JWT token & user data persistence
    }
  }
  
  group APILayer {
    AxiosClient [icon: send] {
      description: api.ts - HTTP client with interceptors
    }
    
    WebSocketClient [icon: radio] {
      description: Live data updates
    }
  }
}

// ============ EXTERNAL SERVICES ============
cloud ExternalServices [icon: cloud, color: cyan] {
  MongoDBAtlas [icon: database] {
    description: Cloud database hosting
  }
  
  GroqAPI [icon: zap] {
    description: AI inference with Llama 3.1 70B
  }
  
  OpenWeatherMap [icon: cloud] {
    description: Real-time weather for Delhi NCR
  }
  
  NASAFIRMS [icon: satellite] {
    description: Fire hotspot detection via satellite
  }
}

// ============ USERS ============
cloud Users [icon: users, color: red] {
  Admin [icon: shield] {
    permissions: Full access, train ML, manage users
  }
  
  Operator [icon: user] {
    permissions: Control sprinklers, view dashboards
  }
  
  Viewer [icon: eye] {
    permissions: Read-only access
  }
}

// ============ CONNECTIONS ============

// Hardware to Backend
ESP32 > SerialPort: Serial USB
DHT22 > ESP32: I2C
MQ2 > ESP32: Analog
RainSensor > ESP32: Digital

// Data Ingestion Flow
SerialPort > SensorIngestion: Raw sensor data
SensorIngestion > DatabaseManager: Store readings
SensorIngestion > WebSocketManager: Broadcast real-time
SensorIngestion > MLPredictor: Trigger analysis
SensorIngestion > AIAgent: Every 30s analysis

// Database connections
DatabaseManager > MongoDB: Motor AsyncIO
MongoDB > Collections: Store/Query

// Routes to Services
AuthRoutes > AuthService: JWT validation
SensorRoutes > DatabaseManager: Query sensor data
DashboardRoutes > DatabaseManager: Stats queries
DashboardRoutes > MLPredictor: Get predictions
AlertRoutes > AlertSystem: Manage alerts
SprinklerRoutes > SprinklerControl: Control commands
MLRoutes > MLPredictor: Fire risk predictions
WeatherRoutes > ExternalIntegrator: Weather data
ZoneRoutes > MultiZoneManager: Multi-zone data
AnalyticsRoutes > AnalyticsEngine: Analytics queries

// Intelligence Layer
MLPredictor > MongoDB: Historical data
AIAgent > MongoDB: Current readings
ExternalIntegrator > MongoDB: Cache weather
AnalyticsEngine > MongoDB: Query patterns

MLPredictor > AlertSystem: Risk predictions
AIAgent > AlertSystem: AI analysis
ExternalIntegrator > AlertSystem: Weather risk
AlertSystem > SprinklerControl: Auto-trigger
AlertSystem > MongoDB: Store alerts

// External API calls
ExternalIntegrator > OpenWeatherMap: Weather API
ExternalIntegrator > NASAFIRMS: Satellite data
AIAgent > GroqAPI: LLM inference
DatabaseManager > MongoDBAtlas: Cloud DB

// Frontend to Backend
AxiosClient > FastAPI: HTTP/REST
WebSocketClient > WebSocketManager: Live updates

LoginPage > AxiosClient: Auth requests
DashboardPage > AxiosClient: Data requests
DashboardPage > WebSocketClient: Real-time updates

LiveSensorData > WebSocketClient: Live feed
SensorChart > AxiosClient: Historical data
HistoricalData > AxiosClient: Query data
AlertsPanel > AxiosClient: Alert CRUD
SprinklerControlUI > AxiosClient: Control commands
AIRecommendations > AxiosClient: AI insights
WeatherSatellite > AxiosClient: Weather data
AnalyticsCharts > AxiosClient: Analytics data

AuthStore > LocalStorage: Persist token
AxiosClient > AuthStore: JWT token header

// User access
Admin > LoginPage: Login
Operator > LoginPage: Login
Viewer > LoginPage: Login
LoginPage > DashboardPage: After auth
```

## Key Features Summary

### 🔧 Hardware Layer
- **ESP32**: WiFi/BLE microcontroller reading sensors every 5 seconds
- **DHT22**: Temperature & humidity monitoring
- **MQ-2**: Smoke and gas detection
- **Rain Sensor**: Precipitation detection

### 🚀 Backend Services
- **FastAPI**: High-performance Python web framework
- **Async Processing**: Motor AsyncIO for MongoDB
- **Real-time**: WebSocket broadcasting
- **Authentication**: JWT-based security

### 🧠 Intelligence Layer
- **ML Models**: Random Forest + Gradient Boosting
- **AI Agent**: Groq Llama 3.1 for risk analysis
- **Weather Integration**: Real-time data for Delhi NCR
- **Analytics**: Pattern detection & forecasting
- **Smart Alerts**: Priority-based notification system
- **Auto Control**: Sprinkler activation based on risk

### 🖥️ Frontend
- **Next.js 14**: Modern React framework
- **Real-time Updates**: WebSocket integration
- **Data Visualization**: Recharts library
- **State Management**: Zustand store
- **Responsive UI**: Tailwind CSS

### 💾 Database
- **MongoDB Atlas**: Cloud-hosted NoSQL database
- **Collections**: sensor_data, users, alerts, sprinkler_logs, predictions, weather_cache
- **Caching**: 10-minute TTL for weather data

### ☁️ External Services
- **OpenWeatherMap**: Weather data API
- **NASA FIRMS**: Satellite fire detection
- **Groq**: AI inference API
- **MongoDB Atlas**: Database hosting

### 👥 User Roles
- **Admin**: Full system control, ML training
- **Operator**: Monitor & control sprinklers
- **Viewer**: Read-only dashboard access

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Hardware** | ESP32, DHT22, MQ-2, Rain Sensor |
| **Backend** | Python 3.8+, FastAPI, Motor, asyncio |
| **ML/AI** | scikit-learn, numpy, Groq API |
| **Database** | MongoDB Atlas (Cloud) |
| **Frontend** | Next.js 14, React 18, TypeScript |
| **Styling** | Tailwind CSS |
| **Charts** | Recharts |
| **State** | Zustand |
| **Auth** | JWT (python-jose) |
| **Real-time** | WebSocket |

## Data Flow

1. **ESP32** reads sensors → Serial USB → **Backend**
2. **Parser** validates → stores in **MongoDB** + broadcasts **WebSocket**
3. **ML Model** analyzes patterns → predicts risk scores
4. **AI Agent** generates recommendations every 30 seconds
5. **Weather API** fetches Delhi data → caches for 10 minutes
6. **Alert System** evaluates inputs → triggers notifications
7. **Sprinkler** auto-activates on high risk
8. **Frontend** receives real-time updates → displays dashboards
9. **Users** authenticate → interact with controls

---

## How to Use This Diagram

### Option 1: Eraser.io (Recommended)
1. Go to https://app.eraser.io/
2. Create new diagram
3. Switch to "Code" mode
4. Paste the entire eraser code block
5. It will render beautifully with proper layout!

### Option 2: Export
- Export as PNG/SVG for presentations
- Share diagram link with team
- Embed in documentation

### Advantages of Eraser Format
✅ Cleaner syntax than Mermaid  
✅ Better automatic layout  
✅ Professional appearance  
✅ Interactive elements  
✅ Easy collaboration  
✅ Version control friendly  
✅ Export to multiple formats  

---

*Smart Forest Fire Prevention System - November 2025*
