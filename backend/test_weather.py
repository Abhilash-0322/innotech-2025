"""
Quick test script to verify OpenWeather API integration
"""
import asyncio
from external_integrator import external_integrator

async def test_weather():
    print("=" * 60)
    print("Testing OpenWeather API Integration")
    print("=" * 60)
    
    # Test getting weather data
    weather = await external_integrator.get_weather_data()
    
    if weather:
        print("\n✅ Weather data retrieved successfully!")
        print(f"Temperature: {weather.temperature}°C")
        print(f"Humidity: {weather.humidity}%")
        print(f"Wind Speed: {weather.wind_speed} m/s")
        print(f"Conditions: {weather.weather_description}")
        print(f"Timestamp: {weather.timestamp}")
    else:
        print("\n❌ Failed to retrieve weather data")
    
    # Test getting location info
    location = external_integrator.get_location_info()
    print(f"\n📍 Configured Location:")
    print(f"Name: {location['name']}")
    print(f"Coordinates: {location['latitude']}, {location['longitude']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_weather())
