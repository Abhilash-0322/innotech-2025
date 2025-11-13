"""
Demo Script - Showcases All Advanced Features
Run this to demonstrate the system's capabilities
"""
import asyncio
import httpx
from datetime import datetime
import json


BASE_URL = "http://localhost:8000"
TOKEN = None  # Will be set after login


async def login():
    """Login and get auth token"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": "admin@forest.com",  # Update with your credentials
                "password": "admin123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            print("✅ Logged in successfully")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False


async def demo_ml_predictions():
    """Demo ML-based fire risk predictions"""
    print("\n" + "="*70)
    print("🤖 DEMO 1: ML-BASED FIRE RISK PREDICTIONS")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Get predictions
        response = await client.get(
            f"{BASE_URL}/api/predictions/fire-risk?hours_ahead=12",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Fire Risk Predictions (Next 12 Hours):")
            
            if 'predictions' in data:
                for pred in data['predictions'][:6]:  # Show first 6 hours
                    print(f"   {pred['hours_ahead']}h ahead: "
                          f"Risk={pred['risk_score']:.1f}%, "
                          f"Level={pred['risk_level'].upper()}, "
                          f"Confidence={pred['confidence']:.2f}")
            else:
                print(f"   {data.get('error', 'No predictions available')}")
        
        # Get feature importance
        response = await client.get(
            f"{BASE_URL}/api/ml/feature-importance",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'features' in data:
                print("\n🎯 Top Important Features:")
                for feat in data['features'][:5]:
                    print(f"   {feat['name']}: {feat['importance']:.3f}")


async def demo_multi_zone():
    """Demo multi-zone sensor network"""
    print("\n" + "="*70)
    print("🗺️  DEMO 2: MULTI-ZONE SENSOR NETWORK")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Get zone comparison
        response = await client.get(
            f"{BASE_URL}/api/zones/comparison",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n📍 Zone Status Comparison:")
            print(f"{'Zone':<20} {'Status':<12} {'Avg Risk':<10} {'Max Risk':<10} {'Nodes'}")
            print("-" * 70)
            
            for zone in data.get('comparison', []):
                print(f"{zone['zone_name']:<20} "
                      f"{zone['status'].upper():<12} "
                      f"{zone['avg_risk']:<10.1f} "
                      f"{zone['max_risk']:<10.1f} "
                      f"{zone['online_nodes']}/{zone['total_nodes']}")
        
        # Get heatmap data
        response = await client.get(
            f"{BASE_URL}/api/zones/heatmap",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n🔥 Heat Map Data:")
            for zone in data.get('heatmap', []):
                risk_bar = "█" * int(zone['risk_score'] / 10)
                print(f"   {zone['zone_name']}: {risk_bar} {zone['risk_score']:.1f}%")
        
        # Get fire spread prediction for highest risk zone
        response = await client.get(
            f"{BASE_URL}/api/zones/ZONE_A/fire-spread",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                print("\n🔥 Fire Spread Prediction (ZONE_A):")
                print(f"   Origin Node: {data['origin_node']}")
                print(f"   Spread Rate: {data['spread_rate_m_per_min']} m/min")
                print(f"   Predicted Radius (30 min): {data['predicted_radius_30min']} m")
                print(f"   Affected Area: {data['affected_area_hectares']} hectares")
                print(f"   At-Risk Nodes: {len(data.get('at_risk_nodes', []))}")


async def demo_external_integration():
    """Demo weather and satellite integration"""
    print("\n" + "="*70)
    print("🛰️  DEMO 3: EXTERNAL DATA INTEGRATION")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Get current weather
        response = await client.get(
            f"{BASE_URL}/api/weather/current",
            headers=headers
        )
        
        if response.status_code == 200:
            weather = response.json()
            print("\n🌤️  Current Weather:")
            print(f"   Temperature: {weather.get('temperature', 'N/A')}°C")
            print(f"   Humidity: {weather.get('humidity', 'N/A')}%")
            print(f"   Wind Speed: {weather.get('wind_speed', 'N/A')} m/s")
            print(f"   UV Index: {weather.get('uv_index', 'N/A')}")
            print(f"   Precipitation: {weather.get('precipitation', 'N/A')} mm")
        
        # Get fire hotspots
        response = await client.get(
            f"{BASE_URL}/api/satellite/fire-hotspots?radius_km=50",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            hotspots = data.get('hotspots', [])
            print(f"\n🛰️  Satellite Fire Hotspots: {len(hotspots)} detected")
            
            for i, hotspot in enumerate(hotspots[:3], 1):
                print(f"   {i}. Distance: {hotspot['distance_km']:.1f}km, "
                      f"Brightness: {hotspot['brightness']:.1f}K, "
                      f"Confidence: {hotspot['confidence']}%, "
                      f"Satellite: {hotspot['satellite']}")
        
        # Get enhanced risk analysis
        response = await client.post(
            f"{BASE_URL}/api/analysis/enhanced-risk",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'enhanced_risk_score' in data:
                print(f"\n📊 Enhanced Risk Analysis:")
                print(f"   Base Risk: {data['base_risk']:.1f}%")
                print(f"   Weather Multiplier: {data['weather_multiplier']}x")
                print(f"   Hotspot Multiplier: {data['hotspot_multiplier']}x")
                print(f"   ✨ Enhanced Risk: {data['enhanced_risk_score']:.1f}%")
                
                print(f"\n⚠️  Risk Factors:")
                for factor in data.get('risk_factors', []):
                    print(f"   • {factor}")


async def demo_analytics():
    """Demo advanced analytics"""
    print("\n" + "="*70)
    print("📈 DEMO 4: ADVANCED ANALYTICS")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Get trend analysis
        for metric in ['temperature', 'humidity', 'fire_risk_score']:
            response = await client.get(
                f"{BASE_URL}/api/analytics/trends?metric={metric}",
                headers=headers
            )
            
            if response.status_code == 200:
                trend = response.json()
                if 'error' not in trend:
                    print(f"\n📊 {metric.upper()} Trend:")
                    print(f"   Current: {trend['current_value']:.1f}")
                    print(f"   24h Avg: {trend['average_24h']:.1f}")
                    print(f"   Direction: {trend['trend_direction'].upper()} "
                          f"(strength: {trend['trend_strength']:.2f})")
                    print(f"   24h Forecast: {trend['forecast_24h']:.1f}")
                    if trend['anomaly_detected']:
                        print(f"   ⚠️  ANOMALY DETECTED!")
        
        # Get pattern detection
        response = await client.get(
            f"{BASE_URL}/api/analytics/patterns",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            patterns = data.get('patterns', [])
            
            if patterns:
                print(f"\n🔍 Detected Patterns: {len(patterns)}")
                for pattern in patterns:
                    print(f"   • {pattern['pattern_type'].upper()} "
                          f"[{pattern['severity'].upper()}]: {pattern['description']}")
            else:
                print("\n🔍 No critical patterns detected (System Normal)")
        
        # Get risk forecast
        response = await client.get(
            f"{BASE_URL}/api/analytics/forecast",
            headers=headers
        )
        
        if response.status_code == 200:
            forecast = response.json()
            print("\n🔮 Fire Risk Forecast:")
            for period, data in forecast.items():
                if isinstance(data, dict):
                    print(f"   {period}: Risk={data.get('risk_score', 0):.1f}%, "
                          f"Confidence={data.get('confidence', 0):.2f}")


async def demo_smart_alerts():
    """Demo smart alert system"""
    print("\n" + "="*70)
    print("🚨 DEMO 5: SMART ALERT SYSTEM")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Get active alerts
        response = await client.get(
            f"{BASE_URL}/api/alerts/active",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            
            print(f"\n🔔 Active Alerts: {len(alerts)}")
            
            for alert in alerts[:5]:  # Show first 5
                priority_emoji = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🟠',
                    'critical': '🔴'
                }.get(alert['priority'], '⚪')
                
                print(f"\n   {priority_emoji} {alert['title']} [{alert['priority'].upper()}]")
                print(f"      {alert['message'][:100]}...")
                print(f"      Time: {alert['timestamp']}")
                print(f"      ID: {alert['alert_id']}")
        
        # Get alert statistics
        response = await client.get(
            f"{BASE_URL}/api/alerts/statistics",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Alert Statistics:")
            print(f"   Total Alerts: {stats.get('total_alerts', 0)}")
            print(f"   Active: {stats.get('active_alerts', 0)}")
            print(f"   Resolved: {stats.get('resolved_alerts', 0)}")
            print(f"   Last 24h: {stats.get('last_24h', 0)}")
            
            by_priority = stats.get('by_priority', {})
            print(f"\n   By Priority:")
            for level, count in by_priority.items():
                print(f"      {level.upper()}: {count}")


async def demo_system_health():
    """Demo system health monitoring"""
    print("\n" + "="*70)
    print("💚 DEMO 6: SYSTEM HEALTH")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        response = await client.get(
            f"{BASE_URL}/api/system/health",
            headers=headers
        )
        
        if response.status_code == 200:
            health = response.json()
            
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'degraded': '⚠️',
                'critical': '🔴'
            }.get(health['status'], '⚪')
            
            print(f"\n{status_emoji} Overall Status: {health['status'].upper()}")
            print(f"   Timestamp: {health['timestamp']}")
            
            components = health.get('components', {})
            print(f"\n📦 Components:")
            print(f"   Database: {components.get('database', 'unknown').upper()}")
            print(f"   ML Model: {components.get('ml_model', 'unknown').upper()}")
            print(f"   Zones: {components.get('zones', 0)}")
            
            nodes = components.get('sensor_nodes', {})
            print(f"\n📡 Sensor Nodes:")
            print(f"   Total: {nodes.get('total', 0)}")
            print(f"   Online: {nodes.get('online', 0)} ✅")
            print(f"   Offline: {nodes.get('offline', 0)} ❌")
            
            alerts = components.get('alerts', {})
            print(f"\n🚨 Current Alerts:")
            print(f"   Active: {alerts.get('active', 0)}")
            print(f"   Critical: {alerts.get('critical', 0)}")


async def main():
    """Run all demos"""
    print("="*70)
    print("🚀 SMART FOREST FIRE PREVENTION SYSTEM - ADVANCED FEATURES DEMO")
    print("="*70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("="*70)
    
    # Login first
    if not await login():
        print("\n❌ Demo aborted: Login failed")
        print("Please ensure:")
        print("1. Backend server is running (uvicorn main:app --reload)")
        print("2. You have created a user account")
        print("3. Update credentials in this script")
        return
    
    try:
        # Run all demos
        await demo_ml_predictions()
        await asyncio.sleep(1)
        
        await demo_multi_zone()
        await asyncio.sleep(1)
        
        await demo_external_integration()
        await asyncio.sleep(1)
        
        await demo_analytics()
        await asyncio.sleep(1)
        
        await demo_smart_alerts()
        await asyncio.sleep(1)
        
        await demo_system_health()
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 Next Steps:")
        print("   1. Review the ADVANCED_FEATURES.md documentation")
        print("   2. Train the ML model: POST /api/ml/train")
        print("   3. Register additional sensor nodes")
        print("   4. Configure email/SMS alerts")
        print("   5. Monitor the real-time dashboard")
        print("\n🏆 Good luck with your presentation!")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
