"""
External Weather & Satellite Data Integration
Integrates with OpenWeatherMap, NASA FIRMS (Fire hotspots), and other APIs
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json


class WeatherData(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_direction: float
    uv_index: float
    visibility: float
    cloud_cover: int
    precipitation: float
    weather_description: str
    timestamp: datetime


class FireHotspot(BaseModel):
    latitude: float
    longitude: float
    brightness: float  # Kelvin
    confidence: int  # 0-100
    scan_time: datetime
    distance_km: float  # Distance from our location
    satellite: str


class ExternalDataIntegrator:
    """
    Integrates external data sources for enhanced fire prediction
    """
    
    def __init__(self, openweather_api_key: Optional[str] = None):
        from config import settings
        
        # Get API key from settings or parameter
        self.openweather_api_key = openweather_api_key or settings.openweather_api_key
        self.nasa_firms_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        self.cache = {}
        self.cache_timeout = 600  # 10 minutes
        
        # Default location from settings
        self.default_location = {
            'latitude': settings.forest_latitude,
            'longitude': settings.forest_longitude,
            'name': settings.forest_location_name
        }
        
        print(f"🌍 External Integrator initialized for: {self.default_location['name']}")
        print(f"📍 Location: {self.default_location['latitude']}, {self.default_location['longitude']}")
        if self.openweather_api_key:
            print(f"✅ OpenWeather API key configured")
        else:
            print(f"⚠️ No OpenWeather API key - will use mock data")
    
    async def get_weather_data(self, latitude: float = None, longitude: float = None) -> Optional[WeatherData]:
        """
        Fetch current weather data from OpenWeatherMap
        """
        # Use default location if not provided
        if latitude is None or longitude is None:
            latitude = self.default_location['latitude']
            longitude = self.default_location['longitude']
            print(f"📍 Using default location: {self.default_location['name']}")
        
        if not self.openweather_api_key:
            print(f"⚠️ No OpenWeather API key configured, using mock data")
            return self._get_mock_weather_data(latitude, longitude)
        
        # Check cache
        cache_key = f"weather_{latitude}_{longitude}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.utcnow() - cached_time).seconds < self.cache_timeout:
                print(f"✅ Using cached weather data (age: {(datetime.utcnow() - cached_time).seconds}s)")
                return cached_data
        
        try:
            print(f"🌍 Fetching real weather data for ({latitude}, {longitude}) from OpenWeatherMap...")
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Fetch UV index separately
                        uv_data = await self._get_uv_index(latitude, longitude, session)
                        
                        weather_data = WeatherData(
                            temperature=data['main']['temp'],
                            humidity=data['main']['humidity'],
                            pressure=data['main']['pressure'],
                            wind_speed=data['wind']['speed'],
                            wind_direction=data['wind'].get('deg', 0),
                            uv_index=uv_data.get('value', 0),
                            visibility=data.get('visibility', 10000) / 1000,  # km
                            cloud_cover=data['clouds']['all'],
                            precipitation=data.get('rain', {}).get('1h', 0),
                            weather_description=data['weather'][0]['description'],
                            timestamp=datetime.utcnow()
                        )
                        
                        # Cache the result
                        self.cache[cache_key] = (weather_data, datetime.utcnow())
                        
                        print(f"✅ Real weather data fetched successfully!")
                        print(f"   📊 Temperature: {weather_data.temperature}°C")
                        print(f"   💧 Humidity: {weather_data.humidity}%")
                        print(f"   🌤️  Conditions: {weather_data.weather_description}")
                        return weather_data
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Weather API error {response.status}: {error_text}")
                        print(f"   Using mock data instead")
                        return self._get_mock_weather_data(latitude, longitude)
        
        except Exception as e:
            print(f"❌ Failed to fetch weather data: {str(e)}")
            print(f"   Using mock data instead")
            return self._get_mock_weather_data(latitude, longitude)
    
    async def _get_uv_index(self, latitude: float, longitude: float, session: aiohttp.ClientSession) -> Dict:
        """Fetch UV index data"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/uvi"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.openweather_api_key
            }
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"⚠️ UV index fetch failed: {e}")
        
        return {'value': 0}
    
    def _get_mock_weather_data(self, latitude: float, longitude: float) -> WeatherData:
        """
        Generate mock weather data when API key is not available
        Useful for testing - simulates Bangalore/forest conditions
        """
        import random
        
        print(f"ℹ️ Using mock weather data for location ({latitude}, {longitude})")
        
        # Simulate realistic Indian forest weather patterns
        return WeatherData(
            temperature=28 + random.uniform(-3, 7),  # 25-35°C typical
            humidity=55 + random.uniform(-15, 25),    # 40-80% range
            pressure=1010 + random.uniform(-5, 5),
            wind_speed=random.uniform(2, 12),         # Light to moderate winds
            wind_direction=random.uniform(0, 360),
            uv_index=random.uniform(3, 10),           # Moderate to very high
            visibility=random.uniform(8, 10),
            cloud_cover=random.randint(10, 60),       # Usually some clouds
            precipitation=random.uniform(0, 3) if random.random() > 0.8 else 0,
            weather_description=random.choice(["Clear sky", "Few clouds", "Scattered clouds", "Partly cloudy"]),
            timestamp=datetime.utcnow()
        )
    
    async def get_fire_hotspots(self, latitude: float = None, longitude: float = None, 
                                radius_km: int = 50) -> List[FireHotspot]:
        """
        Fetch active fire hotspots from NASA FIRMS
        MODIS/VIIRS satellite data
        
        Args:
            latitude: Target latitude (defaults to forest location from env)
            longitude: Target longitude (defaults to forest location from env)
            radius_km: Search radius in kilometers
        
        Note: Requires NASA FIRMS API key (free registration)
        Currently returns mock data for demo purposes
        """
        # Use default location if not provided
        if latitude is None or longitude is None:
            latitude = self.default_location['latitude']
            longitude = self.default_location['longitude']
        
        print(f"🔥 Fetching fire hotspots near ({latitude}, {longitude}) within {radius_km}km")
        
        # For demo purposes, return mock data
        # In production, you would use actual NASA FIRMS API
        return self._get_mock_fire_hotspots(latitude, longitude, radius_km)
    
    def _get_mock_fire_hotspots(self, latitude: float, longitude: float, 
                                radius_km: int) -> List[FireHotspot]:
        """Generate mock fire hotspot data"""
        import random
        
        hotspots = []
        
        # Randomly generate 0-3 nearby hotspots
        num_hotspots = random.randint(0, 3)
        
        for i in range(num_hotspots):
            # Random location within radius
            angle = random.uniform(0, 360)
            distance = random.uniform(5, radius_km)
            
            # Approximate lat/lon offset
            lat_offset = distance * 0.009 * random.uniform(-1, 1)
            lon_offset = distance * 0.009 * random.uniform(-1, 1)
            
            hotspots.append(FireHotspot(
                latitude=latitude + lat_offset,
                longitude=longitude + lon_offset,
                brightness=random.uniform(320, 400),  # Kelvin
                confidence=random.randint(50, 95),
                scan_time=datetime.utcnow() - timedelta(hours=random.randint(0, 12)),
                distance_km=distance,
                satellite=random.choice(['MODIS', 'VIIRS', 'GOES'])
            ))
        
        return sorted(hotspots, key=lambda h: h.distance_km)
    
    async def get_weather_forecast(self, latitude: float = None, longitude: float = None, 
                                   days: int = 3) -> List[Dict]:
        """
        Get weather forecast for next few days
        Useful for long-term fire risk planning
        
        Args:
            latitude: Target latitude (defaults to forest location from env)
            longitude: Target longitude (defaults to forest location from env)
            days: Number of days to forecast
        """
        # Use default location if not provided
        if latitude is None or longitude is None:
            latitude = self.default_location['latitude']
            longitude = self.default_location['longitude']
        
        print(f"📅 Fetching {days}-day forecast for ({latitude}, {longitude})")
        
        if not self.openweather_api_key:
            print("ℹ️ Using mock forecast data (no API key)")
            return self._get_mock_forecast(days)
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.openweather_api_key,
                'units': 'metric',
                'cnt': days * 8  # 3-hour intervals
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        forecast = []
                        for item in data['list']:
                            forecast.append({
                                'timestamp': datetime.fromtimestamp(item['dt']),
                                'temperature': item['main']['temp'],
                                'humidity': item['main']['humidity'],
                                'wind_speed': item['wind']['speed'],
                                'precipitation': item.get('rain', {}).get('3h', 0),
                                'description': item['weather'][0]['description']
                            })
                        
                        print(f"✅ Fetched {len(forecast)} forecast data points")
                        return forecast
        except Exception as e:
            print(f"❌ Failed to fetch forecast: {e}")
        
        return self._get_mock_forecast(days)
    
    def _get_mock_forecast(self, days: int) -> List[Dict]:
        """Generate mock forecast data"""
        import random
        
        forecast = []
        base_temp = 28
        
        for i in range(days * 8):  # 3-hour intervals
            base_temp += random.uniform(-2, 2)
            forecast.append({
                'timestamp': datetime.utcnow() + timedelta(hours=i*3),
                'temperature': max(15, min(45, base_temp)),
                'humidity': random.uniform(30, 80),
                'wind_speed': random.uniform(0, 20),
                'precipitation': random.uniform(0, 10) if random.random() > 0.7 else 0,
                'description': random.choice(['Clear', 'Partly cloudy', 'Cloudy', 'Rain'])
            })
        
        return forecast
    
    async def calculate_enhanced_fire_risk(self, sensor_data: Dict, 
                                          latitude: float, longitude: float) -> Dict:
        """
        Calculate enhanced fire risk using sensor data + external data
        """
        # Get external data
        weather = await self.get_weather_data(latitude, longitude)
        hotspots = await self.get_fire_hotspots(latitude, longitude)
        
        # Base risk from sensors
        base_risk = sensor_data.get('fire_risk_score', 50)
        
        # Weather adjustment factors
        weather_multiplier = 1.0
        if weather:
            # High wind increases risk
            if weather.wind_speed > 20:
                weather_multiplier *= 1.3
            elif weather.wind_speed > 10:
                weather_multiplier *= 1.15
            
            # Low humidity increases risk
            if weather.humidity < 30:
                weather_multiplier *= 1.25
            elif weather.humidity < 50:
                weather_multiplier *= 1.1
            
            # High UV increases risk
            if weather.uv_index > 8:
                weather_multiplier *= 1.15
            
            # No precipitation increases risk
            if weather.precipitation == 0:
                weather_multiplier *= 1.1
        
        # Nearby hotspot adjustment
        hotspot_multiplier = 1.0
        nearby_hotspots = [h for h in hotspots if h.distance_km < 10]
        if nearby_hotspots:
            # Increase risk significantly if active fires nearby
            hotspot_multiplier = 1.5 + (len(nearby_hotspots) * 0.1)
        
        # Calculate final enhanced risk
        enhanced_risk = min(100, base_risk * weather_multiplier * hotspot_multiplier)
        
        return {
            'enhanced_risk_score': round(enhanced_risk, 2),
            'base_risk': base_risk,
            'weather_multiplier': round(weather_multiplier, 2),
            'hotspot_multiplier': round(hotspot_multiplier, 2),
            'weather_data': weather.dict() if weather else None,
            'nearby_hotspots': len(nearby_hotspots),
            'hotspot_details': [h.dict() for h in hotspots[:3]],  # Top 3 closest
            'risk_factors': self._identify_risk_factors(weather, hotspots, sensor_data)
        }
    
    def get_location_info(self) -> Dict:
        """
        Get the configured forest location information
        
        Returns:
            Dict containing location name, latitude, longitude
        """
        return {
            'name': self.default_location['name'],
            'latitude': self.default_location['latitude'],
            'longitude': self.default_location['longitude']
        }
    
    def _identify_risk_factors(self, weather: Optional[WeatherData], 
                               hotspots: List[FireHotspot], sensor_data: Dict) -> List[str]:
        """Identify specific risk factors contributing to fire danger"""
        factors = []
        
        if weather:
            if weather.wind_speed > 15:
                factors.append(f"High wind speed ({weather.wind_speed:.1f} m/s)")
            if weather.humidity < 35:
                factors.append(f"Low humidity ({weather.humidity:.1f}%)")
            if weather.uv_index > 7:
                factors.append(f"High UV index ({weather.uv_index:.1f})")
            if weather.precipitation == 0:
                factors.append("No recent precipitation")
        
        if sensor_data.get('temperature', 0) > 35:
            factors.append(f"High temperature ({sensor_data['temperature']:.1f}°C)")
        
        if sensor_data.get('smoke_level', 0) > 2000:
            factors.append("Elevated smoke levels detected")
        
        nearby = [h for h in hotspots if h.distance_km < 20]
        if nearby:
            factors.append(f"{len(nearby)} fire hotspot(s) within 20km")
        
        return factors


# Global integrator instance
external_integrator = ExternalDataIntegrator()
