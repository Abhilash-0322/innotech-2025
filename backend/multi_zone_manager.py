"""
Multi-Zone Sensor Network Manager
Manages multiple ESP32 sensor nodes across different forest zones
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import numpy as np


class ZoneStatus(str, Enum):
    SAFE = "safe"
    MONITORING = "monitoring"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"
    OFFLINE = "offline"


class SensorZone(BaseModel):
    zone_id: str
    zone_name: str
    latitude: float
    longitude: float
    area_hectares: float
    sensor_nodes: List[str]  # List of node IDs
    status: ZoneStatus = ZoneStatus.SAFE
    last_update: datetime
    average_risk_score: float = 0.0
    max_risk_score: float = 0.0
    active_sprinklers: int = 0
    total_sprinklers: int = 0


class SensorNode(BaseModel):
    node_id: str
    zone_id: str
    name: str
    latitude: float
    longitude: float
    is_online: bool = True
    last_heartbeat: datetime
    current_temperature: float = 0.0
    current_humidity: float = 0.0
    current_smoke: float = 0.0
    current_rain: float = 0.0
    risk_score: float = 0.0
    battery_level: Optional[float] = None  # For solar-powered nodes
    signal_strength: Optional[int] = None  # RSSI


class MultiZoneManager:
    """
    Manages multiple sensor zones and coordinates fire prevention
    across the entire forest network
    """
    
    def __init__(self):
        self.zones: Dict[str, SensorZone] = {}
        self.nodes: Dict[str, SensorNode] = {}
        self._init_default_zones()
    
    def _init_default_zones(self):
        """Initialize default zones (can be overridden from database)"""
        # Example: Create 4 forest zones
        default_zones = [
            {
                "zone_id": "ZONE_A",
                "zone_name": "North Forest Sector",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "area_hectares": 25.0,
                "sensor_nodes": [],
                "total_sprinklers": 10
            },
            {
                "zone_id": "ZONE_B",
                "zone_name": "East Forest Sector",
                "latitude": 12.9656,
                "longitude": 77.6006,
                "area_hectares": 30.0,
                "sensor_nodes": [],
                "total_sprinklers": 12
            },
            {
                "zone_id": "ZONE_C",
                "zone_name": "South Forest Sector",
                "latitude": 12.9626,
                "longitude": 77.5946,
                "area_hectares": 20.0,
                "sensor_nodes": [],
                "total_sprinklers": 8
            },
            {
                "zone_id": "ZONE_D",
                "zone_name": "West Forest Sector",
                "latitude": 12.9716,
                "longitude": 77.5886,
                "area_hectares": 28.0,
                "sensor_nodes": [],
                "total_sprinklers": 11
            }
        ]
        
        for zone_data in default_zones:
            zone_data['last_update'] = datetime.utcnow()
            self.zones[zone_data['zone_id']] = SensorZone(**zone_data)
    
    def register_node(self, node: SensorNode) -> bool:
        """Register a new sensor node"""
        try:
            self.nodes[node.node_id] = node
            
            # Add node to zone
            if node.zone_id in self.zones:
                if node.node_id not in self.zones[node.zone_id].sensor_nodes:
                    self.zones[node.zone_id].sensor_nodes.append(node.node_id)
            
            print(f"✅ Node {node.node_id} registered in {node.zone_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to register node {node.node_id}: {e}")
            return False
    
    def update_node_data(self, node_id: str, sensor_data: Dict) -> bool:
        """Update sensor data for a specific node"""
        if node_id not in self.nodes:
            print(f"⚠️ Unknown node: {node_id}")
            return False
        
        try:
            node = self.nodes[node_id]
            node.last_heartbeat = datetime.utcnow()
            node.is_online = True
            node.current_temperature = sensor_data.get('temperature', 0)
            node.current_humidity = sensor_data.get('humidity', 0)
            node.current_smoke = sensor_data.get('smoke_level', 0)
            node.current_rain = sensor_data.get('rain_level', 0)
            node.risk_score = sensor_data.get('fire_risk_score', 0)
            
            # Update zone statistics
            self._update_zone_stats(node.zone_id)
            
            return True
        except Exception as e:
            print(f"❌ Failed to update node {node_id}: {e}")
            return False
    
    def _update_zone_stats(self, zone_id: str):
        """Recalculate zone statistics based on active nodes"""
        if zone_id not in self.zones:
            return
        
        zone = self.zones[zone_id]
        zone_nodes = [self.nodes[nid] for nid in zone.sensor_nodes if nid in self.nodes]
        
        if not zone_nodes:
            zone.status = ZoneStatus.OFFLINE
            return
        
        # Calculate average and max risk scores
        online_nodes = [n for n in zone_nodes if n.is_online]
        if not online_nodes:
            zone.status = ZoneStatus.OFFLINE
            return
        
        risk_scores = [n.risk_score for n in online_nodes]
        zone.average_risk_score = np.mean(risk_scores)
        zone.max_risk_score = np.max(risk_scores)
        zone.last_update = datetime.utcnow()
        
        # Determine zone status
        if zone.max_risk_score >= 75:
            zone.status = ZoneStatus.CRITICAL
        elif zone.max_risk_score >= 60:
            zone.status = ZoneStatus.DANGER
        elif zone.max_risk_score >= 40:
            zone.status = ZoneStatus.WARNING
        elif zone.max_risk_score >= 20:
            zone.status = ZoneStatus.MONITORING
        else:
            zone.status = ZoneStatus.SAFE
    
    def get_zone_heatmap_data(self) -> List[Dict]:
        """Generate heatmap data for all zones"""
        heatmap_data = []
        
        for zone_id, zone in self.zones.items():
            heatmap_data.append({
                'zone_id': zone_id,
                'zone_name': zone.zone_name,
                'latitude': zone.latitude,
                'longitude': zone.longitude,
                'risk_score': zone.average_risk_score,
                'max_risk': zone.max_risk_score,
                'status': zone.status.value,
                'area': zone.area_hectares,
                'nodes': len(zone.sensor_nodes),
                'online_nodes': len([nid for nid in zone.sensor_nodes 
                                    if nid in self.nodes and self.nodes[nid].is_online])
            })
        
        return heatmap_data
    
    def get_node_positions(self) -> List[Dict]:
        """Get all sensor node positions for mapping"""
        positions = []
        
        for node_id, node in self.nodes.items():
            positions.append({
                'node_id': node_id,
                'name': node.name,
                'zone_id': node.zone_id,
                'latitude': node.latitude,
                'longitude': node.longitude,
                'is_online': node.is_online,
                'risk_score': node.risk_score,
                'temperature': node.current_temperature,
                'humidity': node.current_humidity,
                'smoke': node.current_smoke,
                'battery': node.battery_level,
                'signal': node.signal_strength
            })
        
        return positions
    
    def get_fire_spread_prediction(self, zone_id: str) -> Dict:
        """
        Predict fire spread pattern based on current conditions
        Uses simplified fire spread model
        """
        if zone_id not in self.zones:
            return {'error': 'Zone not found'}
        
        zone = self.zones[zone_id]
        zone_nodes = [self.nodes[nid] for nid in zone.sensor_nodes 
                     if nid in self.nodes and self.nodes[nid].is_online]
        
        if not zone_nodes:
            return {'error': 'No active nodes in zone'}
        
        # Find highest risk node (fire origin)
        origin_node = max(zone_nodes, key=lambda n: n.risk_score)
        
        # Calculate wind direction (simplified - from temperature gradients)
        avg_temp = np.mean([n.current_temperature for n in zone_nodes])
        avg_humidity = np.mean([n.current_humidity for n in zone_nodes])
        
        # Spread rate (meters per minute) based on conditions
        base_spread_rate = 0.5  # meters/min
        temp_factor = max(0, (avg_temp - 25) / 10)  # Increases with temp
        humidity_factor = max(0, (50 - avg_humidity) / 50)  # Increases with dryness
        
        spread_rate = base_spread_rate * (1 + temp_factor) * (1 + humidity_factor)
        
        # Predict affected area in next 30 minutes
        spread_radius_30min = spread_rate * 30  # meters
        
        return {
            'origin_node': origin_node.node_id,
            'origin_coords': {
                'latitude': origin_node.latitude,
                'longitude': origin_node.longitude
            },
            'spread_rate_m_per_min': round(spread_rate, 2),
            'predicted_radius_30min': round(spread_radius_30min, 2),
            'affected_area_hectares': round((spread_radius_30min ** 2 * 3.14159) / 10000, 2),
            'wind_direction': 'N/A',  # Can be enhanced with actual wind data
            'confidence': 0.7,
            'at_risk_nodes': [
                n.node_id for n in zone_nodes 
                if self._calculate_distance(origin_node, n) <= spread_radius_30min
            ]
        }
    
    def _calculate_distance(self, node1: SensorNode, node2: SensorNode) -> float:
        """Calculate distance between two nodes in meters (Haversine formula)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth radius in meters
        
        lat1, lon1 = radians(node1.latitude), radians(node1.longitude)
        lat2, lon2 = radians(node2.latitude), radians(node2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def coordinate_sprinkler_activation(self, zone_id: str) -> Dict:
        """
        Coordinate sprinkler activation across a zone
        Smart activation based on fire spread prediction
        """
        if zone_id not in self.zones:
            return {'error': 'Zone not found'}
        
        spread_prediction = self.get_fire_spread_prediction(zone_id)
        if 'error' in spread_prediction:
            return spread_prediction
        
        zone = self.zones[zone_id]
        at_risk_nodes = spread_prediction.get('at_risk_nodes', [])
        
        # Calculate optimal sprinkler deployment
        # Priority: nodes in predicted fire path
        activation_plan = {
            'zone_id': zone_id,
            'priority_nodes': at_risk_nodes,
            'estimated_water_usage': len(at_risk_nodes) * 100,  # liters/min
            'activation_sequence': [
                {
                    'node_id': node_id,
                    'priority': 1 if node_id in at_risk_nodes[:3] else 2,
                    'delay_seconds': i * 5  # Staggered activation
                }
                for i, node_id in enumerate(at_risk_nodes)
            ],
            'total_sprinklers': len(at_risk_nodes),
            'estimated_duration': 30  # minutes
        }
        
        return activation_plan
    
    def get_zone_comparison(self) -> List[Dict]:
        """Compare all zones side by side"""
        comparison = []
        
        for zone_id, zone in self.zones.items():
            online_nodes = [nid for nid in zone.sensor_nodes 
                           if nid in self.nodes and self.nodes[nid].is_online]
            
            comparison.append({
                'zone_id': zone_id,
                'zone_name': zone.zone_name,
                'status': zone.status.value,
                'avg_risk': round(zone.average_risk_score, 2),
                'max_risk': round(zone.max_risk_score, 2),
                'online_nodes': len(online_nodes),
                'total_nodes': len(zone.sensor_nodes),
                'active_sprinklers': zone.active_sprinklers,
                'area_hectares': zone.area_hectares,
                'last_update': zone.last_update.isoformat()
            })
        
        # Sort by risk score
        comparison.sort(key=lambda x: x['max_risk'], reverse=True)
        
        return comparison
    
    def detect_offline_nodes(self, timeout_minutes: int = 5) -> List[str]:
        """Detect nodes that haven't sent data recently"""
        offline_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        offline_nodes = []
        
        for node_id, node in self.nodes.items():
            if node.last_heartbeat < offline_threshold:
                node.is_online = False
                offline_nodes.append(node_id)
        
        return offline_nodes


# Global multi-zone manager instance
zone_manager = MultiZoneManager()
