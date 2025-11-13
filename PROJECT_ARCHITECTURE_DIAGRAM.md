# Smart Forest Fire Prevention System - Architecture Diagrams

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "IoT Hardware Layer"
        ESP32[ESP32 Microcontroller]
        DHT22[DHT22<br/>Temp & Humidity]
        MQ2[MQ-2<br/>Smoke Sensor]
        RAIN[Rain Sensor]
        ESP32 --> DHT22
        ESP32 --> MQ2
        ESP32 --> RAIN
    end

    subgraph "Backend Services (FastAPI + Python)"
        API[FastAPI Server<br/>Port 8000]
        
        subgraph "Core Modules"
            SI[Sensor Ingestion<br/>Serial/WebSocket]
            DB[Database Manager<br/>MongoDB]
            AUTH[Auth Service<br/>JWT]
        end
        
        subgraph "Intelligence Layer"
            ML[ML Predictor<br/>RandomForest]
            AI[AI Agent<br/>Groq LLM]
            EXT[External Integrator<br/>Weather APIs]
            ANALYTICS[Analytics Engine]
            ALERTS[Smart Alerts]
        end
        
        subgraph "Advanced Features"
            MULTI[Multi-Zone Manager]
            SPRINKLER[Sprinkler Control]
        end
    end

    subgraph "Database Layer"
        MONGO[(MongoDB Atlas<br/>Cloud Database)]
        MONGO_COLLECTIONS[Collections:<br/>- sensor_data<br/>- users<br/>- alerts<br/>- sprinkler_logs]
    end

    subgraph "External APIs"
        WEATHER[OpenWeatherMap API<br/>Real-time Weather]
        FIRMS[NASA FIRMS<br/>Fire Hotspots]
        GROQ[Groq AI<br/>LLM Analysis]
    end

    subgraph "Frontend (Next.js + React)"
        WEB[Web Dashboard<br/>Port 3000]
        
        subgraph "Pages"
            LOGIN[Login/Register]
            DASH[Main Dashboard]
            CHARTS[Charts & Analytics]
            WEATHER_UI[Weather & Satellite]
        end
        
        subgraph "Real-time Updates"
            WS[WebSocket Client]
        end
    end

    subgraph "Users"
        ADMIN[Admin User]
        OPERATOR[Operator]
        VIEWER[Viewer]
    end

    %% Hardware to Backend
    ESP32 -->|Serial USB| SI
    
    %% Core connections
    SI --> API
    SI -->|Store readings| DB
    SI -->|Broadcast| WS
    DB --> MONGO
    AUTH --> MONGO
    
    %% Intelligence connections
    SI -->|Trigger analysis| ML
    SI -->|Real-time data| AI
    ML -->|Predictions| API
    AI -->|Recommendations| API
    EXT -->|Weather data| API
    ANALYTICS -->|Insights| API
    ALERTS -->|Notifications| API
    
    %% External API calls
    EXT --> WEATHER
    EXT --> FIRMS
    AI --> GROQ
    
    %% Advanced features
    MULTI --> API
    SPRINKLER --> API
    
    %% Frontend connections
    WEB -->|HTTP/REST| API
    WEB -->|WebSocket| SI
    API --> WEB
    
    %% User access
    ADMIN --> LOGIN
    OPERATOR --> LOGIN
    VIEWER --> LOGIN
    LOGIN --> DASH
    DASH --> CHARTS
    DASH --> WEATHER_UI
    
    style ESP32 fill:#ff9999
    style API fill:#99ccff
    style ML fill:#99ff99
    style AI fill:#ffcc99
    style MONGO fill:#cc99ff
    style WEB fill:#99ffcc
```

## 2. Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Data Collection"
        SENSORS[IoT Sensors<br/>ESP32 + Sensors]
        SENSORS -->|Serial Port<br/>115200 baud| INGEST[Sensor Ingestion]
    end
    
    subgraph "Processing Pipeline"
        INGEST -->|Store| DB[(MongoDB)]
        INGEST -->|Real-time| WS[WebSocket<br/>Broadcast]
        
        INGEST -->|Every 30s| AI[AI Agent<br/>Risk Analysis]
        DB -->|Historical data| ML[ML Model<br/>Predictions]
        DB -->|Query| ANALYTICS[Analytics<br/>Engine]
        
        EXT[External APIs] -->|Weather| WEATHER_DATA[Weather Data]
        EXT -->|Satellite| HOTSPOTS[Fire Hotspots]
    end
    
    subgraph "Intelligence & Alerts"
        AI -->|Recommendations| ALERT_SYS[Alert System]
        ML -->|Risk Scores| ALERT_SYS
        WEATHER_DATA -->|Conditions| ALERT_SYS
        HOTSPOTS -->|Nearby fires| ALERT_SYS
        
        ALERT_SYS -->|High Risk| SPRINKLER[Auto Sprinkler<br/>Activation]
        ALERT_SYS -->|Store| DB
    end
    
    subgraph "User Interface"
        WS -->|Live updates| FRONTEND[Web Dashboard]
        DB -->|Query results| FRONTEND
        ML -->|Predictions| FRONTEND
        AI -->|Insights| FRONTEND
        ANALYTICS -->|Charts| FRONTEND
        
        FRONTEND -->|User actions| API[REST API]
        API -->|Commands| SPRINKLER
    end
    
    style SENSORS fill:#ff6b6b
    style AI fill:#ffd93d
    style ML fill:#6bcf7f
    style FRONTEND fill:#4d96ff
```

## 3. ML Prediction Pipeline

```mermaid
graph TB
    subgraph "Input Data Collection"
        CURRENT[Current Sensor Reading]
        HISTORY[Historical Data<br/>Last 500 readings]
    end
    
    subgraph "Feature Engineering"
        CURRENT --> FE[Feature Extractor]
        HISTORY --> FE
        
        FE --> BASIC[Basic Features:<br/>- temperature<br/>- humidity<br/>- smoke_level<br/>- rain_level]
        
        FE --> TEMPORAL[Temporal Features:<br/>- hour_of_day<br/>- day_of_week<br/>- month]
        
        FE --> DERIVED[Derived Features:<br/>- temp_change_rate<br/>- humidity_change_rate<br/>- temp_ma_1h<br/>- humidity_ma_1h<br/>- temp_std_1h<br/>- smoke_max_1h]
    end
    
    subgraph "ML Models"
        BASIC --> SCALER[Standard Scaler<br/>Normalization]
        TEMPORAL --> SCALER
        DERIVED --> SCALER
        
        SCALER --> RF[Random Forest<br/>Regressor<br/>100 trees]
        SCALER --> GB[Gradient Boosting<br/>Classifier<br/>Risk Levels]
        
        RF --> RISK_SCORE[Risk Score<br/>0-100]
        GB --> RISK_LEVEL[Risk Level<br/>low/medium/high/critical]
        GB --> CONFIDENCE[Confidence %]
    end
    
    subgraph "Output"
        RISK_SCORE --> PRED[Predictions Array]
        RISK_LEVEL --> PRED
        CONFIDENCE --> PRED
        
        PRED --> API_RESPONSE[API Response:<br/>- predictions for 1-24 hrs<br/>- confidence scores<br/>- feature importance]
    end
    
    style FE fill:#a8e6cf
    style RF fill:#ffd3b6
    style GB fill:#ffaaa5
    style PRED fill:#ff8b94
```

## 4. Authentication & Authorization Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API
    participant Auth
    participant DB
    participant JWT
    
    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>Auth: Validate credentials
    Auth->>DB: Query user
    DB-->>Auth: User data
    Auth->>Auth: Verify password hash
    Auth->>JWT: Generate token
    JWT-->>Auth: JWT token
    Auth-->>API: Token + user info
    API-->>Frontend: Response with token
    Frontend->>Frontend: Store token in localStorage
    
    Note over User,Frontend: Subsequent requests
    
    User->>Frontend: Access protected page
    Frontend->>API: GET /api/sensors/latest<br/>Authorization: Bearer {token}
    API->>Auth: Verify token
    Auth->>JWT: Decode & validate
    JWT-->>Auth: User claims
    Auth->>Auth: Check permissions
    Auth-->>API: User authorized
    API->>DB: Fetch data
    DB-->>API: Sensor data
    API-->>Frontend: Response
    Frontend-->>User: Display data
```

## 5. Real-time WebSocket Communication

```mermaid
sequenceDiagram
    participant ESP32
    participant SensorStream
    participant WebSocket
    participant Frontend1
    participant Frontend2
    participant MongoDB
    
    ESP32->>SensorStream: Serial data<br/>(temp, humidity, smoke)
    SensorStream->>SensorStream: Parse & validate
    
    par Store in DB
        SensorStream->>MongoDB: Insert sensor_data
    and Broadcast to clients
        SensorStream->>WebSocket: Broadcast message
        WebSocket->>Frontend1: Send sensor update
        WebSocket->>Frontend2: Send sensor update
    end
    
    Frontend1->>Frontend1: Update live charts
    Frontend2->>Frontend2: Update dashboard
    
    Note over ESP32,Frontend2: Every ~5 seconds
    
    ESP32->>SensorStream: Next reading
    SensorStream->>MongoDB: Insert
    SensorStream->>WebSocket: Broadcast
    WebSocket->>Frontend1: Update
    WebSocket->>Frontend2: Update
```

## 6. Database Schema

```mermaid
erDiagram
    USERS ||--o{ ALERTS : creates
    USERS {
        ObjectId _id PK
        string email UK
        string full_name
        string hashed_password
        string role
        boolean is_active
        datetime created_at
        datetime last_login
    }
    
    SENSOR_DATA {
        ObjectId _id PK
        float temperature
        float humidity
        float smoke_level
        float rain_level
        boolean rain_detected
        float fire_risk_score
        string risk_level
        datetime timestamp
        string sensor_id
    }
    
    ALERTS {
        ObjectId _id PK
        string title
        string message
        string severity
        string status
        string alert_type
        datetime timestamp
        datetime resolved_at
        ObjectId created_by FK
        dict metadata
    }
    
    SPRINKLER_LOGS {
        ObjectId _id PK
        string action
        string triggered_by
        string reason
        datetime timestamp
        int duration_seconds
        dict sensor_readings
    }
    
    ML_PREDICTIONS {
        ObjectId _id PK
        int hours_ahead
        float risk_score
        string risk_level
        float confidence
        datetime prediction_time
        datetime predicted_for
        array features_used
    }
    
    WEATHER_DATA {
        ObjectId _id PK
        float temperature
        float humidity
        float wind_speed
        float uv_index
        string description
        datetime timestamp
        string location
        dict raw_response
    }
```

## 7. Component Interaction Matrix

```mermaid
graph LR
    subgraph "Routes/Endpoints"
        R_AUTH[/auth/*]
        R_SENSORS[/sensors/*]
        R_DASHBOARD[/dashboard/*]
        R_ALERTS[/alerts/*]
        R_SPRINKLER[/sprinkler/*]
        R_ML[/api/predictions/*]
        R_WEATHER[/api/weather/*]
        R_ZONES[/api/zones/*]
    end
    
    subgraph "Services"
        S_AUTH[Auth Service]
        S_DB[Database]
        S_ML[ML Predictor]
        S_AI[AI Agent]
        S_EXT[External APIs]
        S_ALERTS[Alert System]
        S_MULTI[Multi-Zone]
    end
    
    R_AUTH --> S_AUTH
    R_AUTH --> S_DB
    
    R_SENSORS --> S_DB
    R_SENSORS --> S_AUTH
    
    R_DASHBOARD --> S_DB
    R_DASHBOARD --> S_AUTH
    R_DASHBOARD --> S_ML
    
    R_ALERTS --> S_ALERTS
    R_ALERTS --> S_DB
    R_ALERTS --> S_AUTH
    
    R_SPRINKLER --> S_DB
    R_SPRINKLER --> S_AUTH
    R_SPRINKLER --> S_ALERTS
    
    R_ML --> S_ML
    R_ML --> S_DB
    R_ML --> S_AUTH
    
    R_WEATHER --> S_EXT
    R_WEATHER --> S_AUTH
    
    R_ZONES --> S_MULTI
    R_ZONES --> S_AUTH
    R_ZONES --> S_DB
    
    style S_ML fill:#90ee90
    style S_AI fill:#ffd700
    style S_EXT fill:#87ceeb
```

## 8. Frontend Component Hierarchy

```mermaid
graph TD
    APP[App Root<br/>layout.tsx]
    
    APP --> LOGIN[Login Page<br/>/login]
    APP --> DASHBOARD[Dashboard Page<br/>/dashboard]
    
    DASHBOARD --> STATS[Dashboard Stats Card]
    DASHBOARD --> LIVE[Live Sensor Data]
    DASHBOARD --> CHART[Sensor Chart]
    DASHBOARD --> HIST[Historical Data]
    DASHBOARD --> ALERTS_P[Alerts Panel]
    DASHBOARD --> SPRINKLER_C[Sprinkler Control]
    DASHBOARD --> AI_REC[AI Recommendations]
    DASHBOARD --> WEATHER_SAT[Weather & Satellite]
    
    LIVE --> WS_HOOK[useWebSocket Hook]
    CHART --> CHART_LIB[Recharts Library]
    HIST --> TABLE[Data Table]
    WEATHER_SAT --> MAP[Location Display]
    WEATHER_SAT --> FORECAST[Forecast Cards]
    WEATHER_SAT --> HOTSPOTS[Fire Hotspots List]
    
    subgraph "State Management"
        ZUSTAND[Zustand Store<br/>authStore.ts]
        LOCAL[localStorage<br/>token & user]
    end
    
    LOGIN --> ZUSTAND
    DASHBOARD --> ZUSTAND
    ZUSTAND --> LOCAL
    
    subgraph "API Client"
        API_CLIENT[api.ts]
        AXIOS[Axios Instance]
    end
    
    LIVE --> API_CLIENT
    CHART --> API_CLIENT
    WEATHER_SAT --> API_CLIENT
    API_CLIENT --> AXIOS
    
    style DASHBOARD fill:#e1f5ff
    style WS_HOOK fill:#fff9c4
    style API_CLIENT fill:#c8e6c9
```

## 9. Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_FE[Next.js Dev Server<br/>localhost:3000]
        DEV_BE[FastAPI Server<br/>localhost:8000]
        DEV_DB[MongoDB Atlas<br/>Cloud]
        DEV_SERIAL[ESP32 via USB<br/>/dev/ttyUSB0]
        
        DEV_SERIAL --> DEV_BE
        DEV_BE --> DEV_DB
        DEV_FE --> DEV_BE
    end
    
    subgraph "Production Deployment Options"
        direction TB
        
        subgraph "Option 1: Cloud Hosting"
            VERCEL[Vercel<br/>Frontend Hosting]
            RENDER[Render/Railway<br/>Backend Hosting]
            MONGO_PROD[MongoDB Atlas<br/>Production Cluster]
            
            VERCEL --> RENDER
            RENDER --> MONGO_PROD
        end
        
        subgraph "Option 2: On-Premise"
            NGINX[Nginx<br/>Reverse Proxy]
            FE_BUILD[Next.js Build<br/>Static Files]
            BE_UVICORN[Uvicorn Workers<br/>Gunicorn]
            LOCAL_DB[Local MongoDB<br/>or Atlas]
            
            NGINX --> FE_BUILD
            NGINX --> BE_UVICORN
            BE_UVICORN --> LOCAL_DB
        end
    end
    
    subgraph "External Services"
        OPENWEATHER[OpenWeatherMap API]
        NASA[NASA FIRMS API]
        GROQ_API[Groq AI API]
    end
    
    DEV_BE --> OPENWEATHER
    DEV_BE --> NASA
    DEV_BE --> GROQ_API
    RENDER --> OPENWEATHER
    RENDER --> NASA
    RENDER --> GROQ_API
    BE_UVICORN --> OPENWEATHER
    BE_UVICORN --> NASA
    BE_UVICORN --> GROQ_API
    
    style VERCEL fill:#90ee90
    style RENDER fill:#87ceeb
    style MONGO_PROD fill:#dda0dd
```

## 10. File Structure Tree

```
INNOTECH-2025/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Settings & environment config
│   ├── database.py            # MongoDB connection manager
│   ├── models.py              # Pydantic data models
│   ├── auth.py                # JWT authentication
│   │
│   ├── routes_*.py            # API route modules
│   │   ├── routes_auth.py     # Login, register, user management
│   │   ├── routes_sensors.py  # Sensor data endpoints
│   │   ├── routes_dashboard.py # Dashboard stats & charts
│   │   ├── routes_alerts.py   # Alert management
│   │   ├── routes_sprinkler.py # Sprinkler control
│   │   ├── routes_advanced.py # ML, weather, zones
│   │   └── routes_export.py   # Data export
│   │
│   ├── sensor_ingestion.py   # Serial port data collection
│   ├── ml_predictor.py        # Machine learning models
│   ├── ai_agent.py            # Groq AI integration
│   ├── external_integrator.py # Weather & satellite APIs
│   ├── analytics_engine.py    # Data analytics
│   ├── smart_alerts.py        # Alert generation system
│   ├── multi_zone_manager.py  # Multi-zone monitoring
│   │
│   ├── models/                # Saved ML models
│   │   └── fwi_model.pkl
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   └── .env.example          # Example configuration
│
├── frontend/                  # Next.js React Frontend
│   ├── src/
│   │   ├── app/              # Next.js 14 App Router
│   │   │   ├── layout.tsx    # Root layout
│   │   │   ├── page.tsx      # Home/landing page
│   │   │   ├── login/        # Login page
│   │   │   └── dashboard/    # Main dashboard
│   │   │
│   │   ├── components/       # React components
│   │   │   ├── LiveSensorData.tsx
│   │   │   ├── SensorChart.tsx
│   │   │   ├── HistoricalData.tsx
│   │   │   ├── AlertsPanel.tsx
│   │   │   ├── SprinklerControl.tsx
│   │   │   ├── AIRecommendationsSidebar.tsx
│   │   │   ├── WeatherSatellite.tsx
│   │   │   └── ...
│   │   │
│   │   ├── lib/              # Utilities
│   │   │   ├── api.ts        # API client (Axios)
│   │   │   └── utils.ts      # Helper functions
│   │   │
│   │   └── store/            # State management
│   │       └── authStore.ts  # Zustand auth store
│   │
│   ├── package.json          # NPM dependencies
│   ├── tailwind.config.js    # Tailwind CSS config
│   └── next.config.js        # Next.js configuration
│
├── docs/                      # Documentation
│   ├── API_DOCS.md
│   ├── ARCHITECTURE.md
│   ├── QUICKSTART.md
│   └── WEATHER_INTEGRATION_COMPLETE.md
│
└── README.md                 # Project overview
```

## Technology Stack Summary

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: MongoDB (Motor async driver)
- **ML**: scikit-learn, numpy, pandas
- **AI**: Groq API (Llama 3.1)
- **External APIs**: OpenWeatherMap, NASA FIRMS
- **Real-time**: WebSocket, asyncio
- **Auth**: JWT (python-jose, passlib)

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP**: Axios
- **State**: Zustand
- **Icons**: Lucide React

### Hardware
- **Microcontroller**: ESP32
- **Sensors**: DHT22, MQ-2, Rain Sensor
- **Communication**: Serial (USB)

### Infrastructure
- **Database**: MongoDB Atlas (Cloud)
- **AI**: Groq Cloud API
- **Weather**: OpenWeatherMap API
- **Version Control**: Git + GitHub

---

*Generated: November 2025*
*Project: Smart Forest Fire Prevention System*
