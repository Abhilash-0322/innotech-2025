"""
Advanced Analytics Engine
Provides trend analysis, pattern recognition, and insights
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from pydantic import BaseModel


class TrendAnalysis(BaseModel):
    metric: str
    current_value: float
    average_24h: float
    average_7d: float
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    forecast_24h: float
    anomaly_detected: bool


class PatternRecognition(BaseModel):
    pattern_type: str
    confidence: float
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    severity: str


class AdvancedAnalytics:
    """
    Advanced analytics for fire risk prediction and insights
    """
    
    def __init__(self):
        self.data_buffer = defaultdict(list)  # Store recent data
        self.max_buffer_size = 10080  # 1 week at 1 min intervals
    
    def add_data_point(self, timestamp: datetime, data: Dict):
        """Add a new data point to the analytics buffer"""
        for key, value in data.items():
            if isinstance(value, (int, float)):
                self.data_buffer[key].append({
                    'timestamp': timestamp,
                    'value': value
                })
                
                # Trim buffer if too large
                if len(self.data_buffer[key]) > self.max_buffer_size:
                    self.data_buffer[key] = self.data_buffer[key][-self.max_buffer_size:]
    
    def analyze_trends(self, metric: str = 'temperature') -> Optional[TrendAnalysis]:
        """
        Analyze trends for a specific metric
        Uses moving averages and linear regression
        """
        if metric not in self.data_buffer or len(self.data_buffer[metric]) < 100:
            return None
        
        data = self.data_buffer[metric]
        current_value = data[-1]['value']
        
        # Calculate moving averages
        recent_24h = [d['value'] for d in data if 
                     (data[-1]['timestamp'] - d['timestamp']).total_seconds() <= 86400]
        recent_7d = [d['value'] for d in data if 
                    (data[-1]['timestamp'] - d['timestamp']).total_seconds() <= 604800]
        
        avg_24h = np.mean(recent_24h) if recent_24h else current_value
        avg_7d = np.mean(recent_7d) if recent_7d else current_value
        
        # Calculate trend using linear regression
        if len(recent_24h) > 10:
            x = np.arange(len(recent_24h))
            y = np.array(recent_24h)
            slope, intercept = np.polyfit(x, y, 1)
            
            # Forecast 24 hours ahead
            forecast_24h = intercept + slope * (len(recent_24h) + 1440)  # +24 hours
            
            # Determine trend direction and strength
            if abs(slope) < 0.01:
                trend_direction = "stable"
                trend_strength = 0.0
            elif slope > 0:
                trend_direction = "increasing"
                trend_strength = min(1.0, abs(slope) * 10)
            else:
                trend_direction = "decreasing"
                trend_strength = min(1.0, abs(slope) * 10)
            
            # Detect anomalies (values > 2 std deviations from mean)
            std_dev = np.std(recent_24h)
            anomaly_detected = abs(current_value - avg_24h) > (2 * std_dev)
        else:
            forecast_24h = current_value
            trend_direction = "stable"
            trend_strength = 0.0
            anomaly_detected = False
        
        return TrendAnalysis(
            metric=metric,
            current_value=current_value,
            average_24h=avg_24h,
            average_7d=avg_7d,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            forecast_24h=forecast_24h,
            anomaly_detected=anomaly_detected
        )
    
    def detect_patterns(self) -> List[PatternRecognition]:
        """
        Detect common fire risk patterns
        """
        patterns = []
        
        # Pattern 1: Continuous high temperature + low humidity
        temp_data = self.data_buffer.get('temperature', [])
        humidity_data = self.data_buffer.get('humidity', [])
        
        if temp_data and humidity_data:
            recent_temps = [d['value'] for d in temp_data[-60:]]  # Last hour
            recent_humidity = [d['value'] for d in humidity_data[-60:]]
            
            if len(recent_temps) > 30:
                avg_temp = np.mean(recent_temps)
                avg_humidity = np.mean(recent_humidity)
                
                if avg_temp > 35 and avg_humidity < 30:
                    patterns.append(PatternRecognition(
                        pattern_type="extreme_dryness",
                        confidence=0.9,
                        description="Sustained high temperature with low humidity",
                        start_time=temp_data[-60]['timestamp'],
                        end_time=None,
                        severity="high"
                    ))
        
        # Pattern 2: Rapid temperature increase
        if temp_data and len(temp_data) > 30:
            recent = [d['value'] for d in temp_data[-30:]]
            older = [d['value'] for d in temp_data[-60:-30]] if len(temp_data) > 60 else recent
            
            temp_increase = np.mean(recent) - np.mean(older)
            if temp_increase > 5:  # 5°C increase in 30 minutes
                patterns.append(PatternRecognition(
                    pattern_type="rapid_heating",
                    confidence=0.85,
                    description=f"Temperature increased by {temp_increase:.1f}°C in 30 minutes",
                    start_time=temp_data[-30]['timestamp'],
                    end_time=temp_data[-1]['timestamp'],
                    severity="medium"
                ))
        
        # Pattern 3: Smoke spike detection
        smoke_data = self.data_buffer.get('smoke_level', [])
        if smoke_data and len(smoke_data) > 10:
            recent_smoke = [d['value'] for d in smoke_data[-10:]]
            baseline = np.mean([d['value'] for d in smoke_data[-60:-10]]) if len(smoke_data) > 60 else 0
            
            current_smoke = recent_smoke[-1]
            if current_smoke > baseline * 2 and current_smoke > 1500:
                patterns.append(PatternRecognition(
                    pattern_type="smoke_spike",
                    confidence=0.95,
                    description=f"Sudden smoke increase: {current_smoke:.0f} (baseline: {baseline:.0f})",
                    start_time=smoke_data[-10]['timestamp'],
                    end_time=None,
                    severity="critical"
                ))
        
        # Pattern 4: Diurnal risk pattern (time of day analysis)
        if temp_data:
            current_hour = datetime.utcnow().hour
            if 12 <= current_hour <= 16:  # Peak heat hours
                avg_temp = np.mean([d['value'] for d in temp_data[-60:]])
                if avg_temp > 33:
                    patterns.append(PatternRecognition(
                        pattern_type="peak_heat_hours",
                        confidence=0.8,
                        description="High risk during peak heat hours (12pm-4pm)",
                        start_time=datetime.utcnow().replace(hour=12, minute=0),
                        end_time=datetime.utcnow().replace(hour=16, minute=0),
                        severity="medium"
                    ))
        
        return patterns
    
    def generate_insights(self) -> Dict:
        """
        Generate comprehensive insights from analytics
        """
        insights = {
            'trends': {},
            'patterns': [],
            'recommendations': [],
            'risk_forecast': {},
            'statistics': {}
        }
        
        # Analyze trends for key metrics
        for metric in ['temperature', 'humidity', 'smoke_level', 'fire_risk_score']:
            trend = self.analyze_trends(metric)
            if trend:
                insights['trends'][metric] = trend.dict()
        
        # Detect patterns
        patterns = self.detect_patterns()
        insights['patterns'] = [p.dict() for p in patterns]
        
        # Generate recommendations based on patterns
        if patterns:
            for pattern in patterns:
                if pattern.pattern_type == "extreme_dryness":
                    insights['recommendations'].append({
                        'priority': 'high',
                        'action': 'Increase monitoring frequency to every 5 minutes',
                        'reason': 'Extreme dry conditions detected'
                    })
                    insights['recommendations'].append({
                        'priority': 'high',
                        'action': 'Pre-position firefighting resources',
                        'reason': 'High probability of ignition'
                    })
                
                elif pattern.pattern_type == "smoke_spike":
                    insights['recommendations'].append({
                        'priority': 'critical',
                        'action': 'Immediate investigation required',
                        'reason': 'Sudden smoke increase may indicate fire ignition'
                    })
                    insights['recommendations'].append({
                        'priority': 'critical',
                        'action': 'Activate sprinklers in affected zone',
                        'reason': 'Smoke levels exceed safety threshold'
                    })
        
        # Calculate statistics
        insights['statistics'] = self._calculate_statistics()
        
        # Risk forecast
        insights['risk_forecast'] = self._generate_risk_forecast()
        
        return insights
    
    def _calculate_statistics(self) -> Dict:
        """Calculate key statistics from historical data"""
        stats = {}
        
        for metric in ['temperature', 'humidity', 'smoke_level']:
            if metric in self.data_buffer and self.data_buffer[metric]:
                values = [d['value'] for d in self.data_buffer[metric][-1440:]]  # Last 24h
                
                if values:
                    stats[metric] = {
                        'current': values[-1],
                        'min_24h': np.min(values),
                        'max_24h': np.max(values),
                        'avg_24h': np.mean(values),
                        'std_24h': np.std(values),
                        'percentile_95': np.percentile(values, 95)
                    }
        
        return stats
    
    def _generate_risk_forecast(self) -> Dict:
        """Generate fire risk forecast for next 24 hours"""
        forecast = {
            'next_1h': {'risk_score': 0, 'confidence': 0},
            'next_6h': {'risk_score': 0, 'confidence': 0},
            'next_24h': {'risk_score': 0, 'confidence': 0}
        }
        
        # Use trend analysis for forecasting
        risk_trend = self.analyze_trends('fire_risk_score')
        temp_trend = self.analyze_trends('temperature')
        
        if risk_trend and temp_trend:
            current_risk = risk_trend.current_value
            
            # Simple linear extrapolation
            if risk_trend.trend_direction == "increasing":
                forecast['next_1h']['risk_score'] = min(100, current_risk + 2)
                forecast['next_6h']['risk_score'] = min(100, current_risk + 8)
                forecast['next_24h']['risk_score'] = min(100, risk_trend.forecast_24h)
            elif risk_trend.trend_direction == "decreasing":
                forecast['next_1h']['risk_score'] = max(0, current_risk - 2)
                forecast['next_6h']['risk_score'] = max(0, current_risk - 8)
                forecast['next_24h']['risk_score'] = max(0, risk_trend.forecast_24h)
            else:
                forecast['next_1h']['risk_score'] = current_risk
                forecast['next_6h']['risk_score'] = current_risk
                forecast['next_24h']['risk_score'] = current_risk
            
            # Confidence based on trend strength and data availability
            base_confidence = 0.7 if len(self.data_buffer['fire_risk_score']) > 500 else 0.5
            forecast['next_1h']['confidence'] = base_confidence + 0.2
            forecast['next_6h']['confidence'] = base_confidence
            forecast['next_24h']['confidence'] = base_confidence - 0.1
        
        return forecast
    
    def get_historical_comparison(self, days_back: int = 7) -> Dict:
        """
        Compare current conditions with historical data
        """
        comparison = {
            'current_vs_weekly_avg': {},
            'peak_risk_times': [],
            'safest_times': []
        }
        
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        for metric in ['temperature', 'humidity', 'fire_risk_score']:
            if metric in self.data_buffer:
                historical = [d for d in self.data_buffer[metric] 
                            if d['timestamp'] >= cutoff]
                
                if historical:
                    historical_values = [d['value'] for d in historical]
                    current_value = historical[-1]['value']
                    avg_value = np.mean(historical_values)
                    
                    comparison['current_vs_weekly_avg'][metric] = {
                        'current': current_value,
                        'weekly_avg': avg_value,
                        'difference': current_value - avg_value,
                        'percentile': self._calculate_percentile(current_value, historical_values)
                    }
        
        return comparison
    
    def _calculate_percentile(self, value: float, dataset: List[float]) -> int:
        """Calculate percentile rank of a value in dataset"""
        sorted_data = sorted(dataset)
        rank = sum(1 for v in sorted_data if v <= value)
        return int((rank / len(sorted_data)) * 100)


# Global analytics instance
analytics_engine = AdvancedAnalytics()
