"""
Advanced Features API Routes
Exposes ML predictions, multi-zone management, analytics, and more
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import numpy as np
import random

from ml_predictor import predictor
from multi_zone_manager import zone_manager, SensorNode, ZoneStatus
from external_integrator import external_integrator
from analytics_engine import analytics_engine
from smart_alerts import alert_system, AlertPriority
from database import get_database
from auth import get_current_user

router = APIRouter()


# ============= Helper Functions =============

def generate_mock_predictions(hours_ahead: int = 6):
    """
    Generate realistic mock predictions for demo purposes
    Used when model is not trained or no data is available
    """
    predictions = []
    base_risk = random.uniform(20, 45)  # Base risk score
    
    for h in range(1, min(hours_ahead + 1, 25)):
        # Add some variation over time
        risk_score = base_risk + random.uniform(-5, 10) + (h * 0.5)
        risk_score = np.clip(risk_score, 0, 100)
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = 'critical'
        elif risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        predictions.append({
            'hours_ahead': h,
            'timestamp': (datetime.utcnow() + timedelta(hours=h)).isoformat(),
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'confidence': random.uniform(0.75, 0.95)
        })
    
    return {
        'predictions': predictions,
        'model_version': 'mock-1.0',
        'features_used': [
            'temperature', 'humidity', 'smoke_level', 'rain_level',
            'hour_of_day', 'day_of_week', 'month',
            'temp_change_rate', 'humidity_change_rate',
            'temp_ma_1h', 'humidity_ma_1h', 'temp_std_1h', 'smoke_max_1h'
        ],
        'note': 'Using mock predictions - model training recommended'
    }


# ============= ML Predictions =============

@router.get("/api/predictions/fire-risk")
async def get_fire_risk_prediction(
    hours_ahead: int = 6,
    current_user: dict = Depends(get_current_user)
):
    """
    Get ML-based fire risk predictions for next N hours
    Uses trained ML model if available, otherwise returns mock predictions
    """
    try:
        # Get recent sensor history from database
        db = get_database()
        sensor_history = await db.sensor_data.find().sort("timestamp", -1).limit(500).to_list(500)
        
        if not sensor_history:
            print("⚠️ No sensor data available, returning mock predictions")
            return generate_mock_predictions(hours_ahead)
        
        print(f"📊 Found {len(sensor_history)} sensor readings for prediction")
        
        # Convert to list of dicts
        history = [
            {
                'temperature': s.get('temperature', 0),
                'humidity': s.get('humidity', 0),
                'smoke_level': s.get('smoke_level', 0),
                'rain_level': s.get('rain_level', 0),
                'timestamp': s.get('timestamp')
            }
            for s in sensor_history
        ]
        
        # Get predictions from ML model
        predictions = predictor.predict(history, hours_ahead)
        
        # If model not trained, return mock predictions
        if 'error' in predictions:
            if 'not trained' in predictions.get('error', '').lower():
                print("⚠️ ML model not trained yet, returning mock predictions")
                return generate_mock_predictions(hours_ahead)
            else:
                print(f"❌ Prediction error: {predictions['error']}")
                return generate_mock_predictions(hours_ahead)
        
        print(f"✅ Generated {len(predictions.get('predictions', []))} ML predictions")
        return predictions
    
    except Exception as e:
        # On any error, return mock predictions for demo purposes
        import traceback
        print(f"❌ Error in fire-risk prediction: {str(e)}")
        print(traceback.format_exc())
        return generate_mock_predictions(hours_ahead)

        print(f"Error in fire-risk prediction: {str(e)}")
        print(traceback.format_exc())
        return generate_mock_predictions(hours_ahead)


@router.post("/api/ml/train")
async def train_ml_model(current_user: dict = Depends(get_current_user)):
    """
    Train/retrain the ML model with historical data
    Requires admin role
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        db = await get_database()
        
        # Get historical sensor data
        sensor_data = await db.sensor_data.find().sort("timestamp", -1).limit(10000).to_list(10000)
        
        if len(sensor_data) < 100:
            return {"error": "Insufficient training data. Need at least 100 samples."}
        
        # Prepare training data
        sensor_history = [
            {
                'temperature': s.get('temperature', 0),
                'humidity': s.get('humidity', 0),
                'smoke_level': s.get('smoke_level', 0),
                'rain_level': s.get('rain_level', 0),
                'timestamp': s.get('timestamp')
            }
            for s in sensor_data
        ]
        
        risk_scores = [s.get('fire_risk_score', 0) for s in sensor_data]
        risk_levels = [s.get('risk_level', 'low') for s in sensor_data]
        
        # Train model
        success = predictor.train(sensor_history, risk_scores, risk_levels)
        
        if success:
            return {
                "message": "Model trained successfully",
                "training_samples": len(sensor_data),
                "model_version": "1.0"
            }
        else:
            return {"error": "Training failed"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ml/status")
async def get_ml_status(current_user: dict = Depends(get_current_user)):
    """Get ML model training status and info"""
    try:
        db = get_database()
        sensor_count = await db.sensor_data.count_documents({})
        
        return {
            "is_trained": predictor.is_trained,
            "model_path": str(predictor.model_path),
            "model_exists": predictor.model_path.exists(),
            "available_data": sensor_count,
            "required_data": 100,
            "can_train": sensor_count >= 100,
            "features": predictor.feature_columns,
            "status": "ready" if predictor.is_trained else "not_trained"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ml/feature-importance")
async def get_feature_importance(current_user: dict = Depends(get_current_user)):
    """Get feature importance from trained ML model"""
    try:
        importance = predictor.get_feature_importance()
        
        if not importance:
            return {"error": "Model not trained yet"}
        
        # Sort by importance
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "features": [
                {"name": feat, "importance": float(imp)}
                for feat, imp in sorted_features
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Multi-Zone Management =============

@router.get("/api/zones")
async def get_all_zones(current_user: dict = Depends(get_current_user)):
    """Get all sensor zones"""
    try:
        zones = [zone.dict() for zone in zone_manager.zones.values()]
        return {"zones": zones}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/zones/heatmap")
async def get_zone_heatmap(current_user: dict = Depends(get_current_user)):
    """Get heatmap data for all zones"""
    try:
        heatmap_data = zone_manager.get_zone_heatmap_data()
        return {"heatmap": heatmap_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/zones/comparison")
async def get_zone_comparison(current_user: dict = Depends(get_current_user)):
    """Compare all zones side by side"""
    try:
        comparison = zone_manager.get_zone_comparison()
        return {"comparison": comparison}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/zones/{zone_id}/fire-spread")
async def get_fire_spread_prediction(
    zone_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get fire spread prediction for a specific zone"""
    try:
        prediction = zone_manager.get_fire_spread_prediction(zone_id)
        return prediction
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/zones/{zone_id}/activate-sprinklers")
async def activate_zone_sprinklers(
    zone_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Activate sprinklers in a specific zone with smart coordination"""
    try:
        activation_plan = zone_manager.coordinate_sprinkler_activation(zone_id)
        
        if 'error' in activation_plan:
            raise HTTPException(status_code=404, detail=activation_plan['error'])
        
        return {
            "message": f"Sprinkler activation initiated for {zone_id}",
            "plan": activation_plan
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/nodes")
async def get_all_nodes(current_user: dict = Depends(get_current_user)):
    """Get all sensor nodes with their positions"""
    try:
        nodes = zone_manager.get_node_positions()
        return {"nodes": nodes}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/nodes/register")
async def register_sensor_node(
    node_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Register a new sensor node"""
    try:
        node = SensorNode(
            node_id=node_data['node_id'],
            zone_id=node_data['zone_id'],
            name=node_data['name'],
            latitude=node_data['latitude'],
            longitude=node_data['longitude'],
            last_heartbeat=datetime.utcnow()
        )
        
        success = zone_manager.register_node(node)
        
        if success:
            return {"message": f"Node {node.node_id} registered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register node")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= External Data Integration =============

@router.get("/api/weather/current")
async def get_current_weather(
    latitude: float = 12.9716,
    longitude: float = 77.5946,
    current_user: dict = Depends(get_current_user)
):
    """Get current weather data from external API"""
    try:
        weather = await external_integrator.get_weather_data(latitude, longitude)
        
        if weather:
            return weather.dict()
        else:
            return {"error": "Failed to fetch weather data"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/weather/forecast")
async def get_weather_forecast(
    latitude: float = 12.9716,
    longitude: float = 77.5946,
    days: int = 3,
    current_user: dict = Depends(get_current_user)
):
    """Get weather forecast"""
    try:
        forecast = await external_integrator.get_weather_forecast(latitude, longitude, days)
        return {"forecast": forecast}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/satellite/fire-hotspots")
async def get_fire_hotspots(
    latitude: float = 12.9716,
    longitude: float = 77.5946,
    radius_km: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get nearby fire hotspots from satellite data"""
    try:
        hotspots = await external_integrator.get_fire_hotspots(latitude, longitude, radius_km)
        return {"hotspots": [h.dict() for h in hotspots]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/external/location")
async def get_location_info(current_user: dict = Depends(get_current_user)):
    """
    Get configured forest location information
    Returns the default monitoring location (name, latitude, longitude)
    """
    try:
        location = external_integrator.get_location_info()
        return location
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analysis/enhanced-risk")
async def get_enhanced_risk_analysis(current_user: dict = Depends(get_current_user)):
    """
    Get enhanced fire risk analysis combining sensor data + external data
    """
    try:
        db = await get_database()
        latest_sensor = await db.sensor_data.find_one(sort=[("timestamp", -1)])
        
        if not latest_sensor:
            return {"error": "No sensor data available"}
        
        # Get enhanced analysis
        analysis = await external_integrator.calculate_enhanced_fire_risk(
            latest_sensor,
            latitude=12.9716,
            longitude=77.5946
        )
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Advanced Analytics =============

@router.get("/api/analytics/trends")
async def get_trend_analysis(
    metric: str = "temperature",
    current_user: dict = Depends(get_current_user)
):
    """Get trend analysis for a specific metric"""
    try:
        trend = analytics_engine.analyze_trends(metric)
        
        if trend:
            return trend.dict()
        else:
            return {"error": f"Insufficient data for {metric}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/patterns")
async def get_pattern_detection(current_user: dict = Depends(get_current_user)):
    """Detect fire risk patterns in current data"""
    try:
        patterns = analytics_engine.detect_patterns()
        return {"patterns": [p.dict() for p in patterns]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/insights")
async def get_analytics_insights(current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics insights"""
    try:
        insights = analytics_engine.generate_insights()
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/forecast")
async def get_risk_forecast(current_user: dict = Depends(get_current_user)):
    """Get fire risk forecast for next 24 hours"""
    try:
        insights = analytics_engine.generate_insights()
        return insights.get('risk_forecast', {})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/historical-comparison")
async def get_historical_comparison(
    days_back: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Compare current conditions with historical data"""
    try:
        comparison = analytics_engine.get_historical_comparison(days_back)
        return comparison
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Smart Alerts =============

@router.get("/api/alerts/active")
async def get_active_alerts(
    priority: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all active alerts"""
    try:
        priority_enum = AlertPriority(priority) if priority else None
        alerts = alert_system.get_active_alerts(priority_enum)
        return {"alerts": [a.dict() for a in alerts]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge an alert"""
    try:
        success = alert_system.acknowledge_alert(alert_id, current_user.get('email', 'Unknown'))
        
        if success:
            return {"message": f"Alert {alert_id} acknowledged"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Resolve an alert"""
    try:
        success = alert_system.resolve_alert(alert_id, current_user.get('email', 'Unknown'))
        
        if success:
            return {"message": f"Alert {alert_id} resolved"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/alerts/statistics")
async def get_alert_statistics(current_user: dict = Depends(get_current_user)):
    """Get alert system statistics"""
    try:
        stats = alert_system.get_alert_statistics()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= System Health & Monitoring =============

@router.get("/api/system/health")
async def get_system_health(current_user: dict = Depends(get_current_user)):
    """Get overall system health status"""
    try:
        offline_nodes = zone_manager.detect_offline_nodes(timeout_minutes=5)
        active_alerts = alert_system.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.priority == AlertPriority.CRITICAL]
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "online",
                "ml_model": "trained" if predictor.is_trained else "not_trained",
                "zones": len(zone_manager.zones),
                "sensor_nodes": {
                    "total": len(zone_manager.nodes),
                    "online": len(zone_manager.nodes) - len(offline_nodes),
                    "offline": len(offline_nodes)
                },
                "alerts": {
                    "active": len(active_alerts),
                    "critical": len(critical_alerts)
                }
            }
        }
        
        # Determine overall status
        if critical_alerts:
            health_status["status"] = "critical"
        elif len(offline_nodes) > len(zone_manager.nodes) / 2:
            health_status["status"] = "degraded"
        elif not predictor.is_trained:
            health_status["status"] = "warning"
        
        return health_status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
