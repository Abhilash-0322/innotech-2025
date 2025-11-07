#!/bin/bash

# Smart Forest Fire Prevention System - Sensor Stream Starter

echo "🔥 Starting Smart Forest Fire Prevention System - Sensor Stream"
echo "==============================================================="
echo ""

cd "$(dirname "$0")/backend"

echo "📡 Starting real-time sensor data streaming..."
echo "This will read from ESP32 and stream to the dashboard"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 start_sensor_stream.py
