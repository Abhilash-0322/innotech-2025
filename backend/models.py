from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class SprinklerStatus(str, Enum):
    OFF = "off"
    ON = "on"
    AUTO = "auto"


# Sensor Data Models
class SensorData(BaseModel):
    temperature: float
    humidity: float
    smoke_level: float
    rain_level: float
    rain_detected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SensorDataDB(SensorData):
    id: Optional[str] = Field(alias="_id")
    fire_risk_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None


# Fire Risk Analysis
class FireRiskAnalysis(BaseModel):
    risk_score: float  # 0-100
    risk_level: RiskLevel
    reasoning: str
    recommendations: List[str]
    should_activate_sprinkler: bool
    confidence: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FireRiskAnalysisDB(FireRiskAnalysis):
    id: Optional[str] = Field(alias="_id")
    sensor_data_id: Optional[str] = None


# Alert Models
class Alert(BaseModel):
    title: str
    message: str
    severity: RiskLevel
    status: AlertStatus = AlertStatus.ACTIVE
    sensor_data: Optional[SensorData] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertDB(Alert):
    id: Optional[str] = Field(alias="_id")
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


# Sprinkler Control
class SprinklerControl(BaseModel):
    status: SprinklerStatus
    manual_override: bool = False
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    reason: Optional[str] = None


class SprinklerControlDB(SprinklerControl):
    id: Optional[str] = Field(alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# User Models
class User(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "user"  # user, admin
    is_active: bool = True


class UserInDB(User):
    id: Optional[str] = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Dashboard Statistics
class DashboardStats(BaseModel):
    current_temperature: float
    current_humidity: float
    current_smoke: float
    current_risk_level: RiskLevel
    current_risk_score: float
    active_alerts: int
    sprinkler_status: SprinklerStatus
    total_readings_today: int
    average_temp_today: float
    max_risk_today: float
