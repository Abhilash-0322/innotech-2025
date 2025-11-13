"""
Smart Alert & Notification System
Multi-channel alerts with intelligent escalation
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SIREN = "siren"
    DASHBOARD = "dashboard"


class AlertRule(BaseModel):
    rule_id: str
    name: str
    condition: str  # e.g., "risk_score > 75"
    priority: AlertPriority
    channels: List[NotificationChannel]
    cooldown_minutes: int = 15  # Prevent spam
    enabled: bool = True


class AlertMessage(BaseModel):
    alert_id: str
    title: str
    message: str
    priority: AlertPriority
    source: str
    data: Dict
    channels: List[NotificationChannel]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False


class SmartAlertSystem:
    """
    Intelligent alert system with multi-channel notifications
    and escalation workflows
    """
    
    def __init__(self):
        self.alert_rules = self._init_default_rules()
        self.active_alerts: Dict[str, AlertMessage] = {}
        self.alert_history: List[AlertMessage] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Email configuration (configure in settings)
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = None  # Set from environment
        self.smtp_password = None
        self.from_email = "forest-fire-alert@example.com"
        
        # Recipient lists
        self.email_recipients = []
        self.sms_recipients = []
        self.webhook_urls = []
    
    def _init_default_rules(self) -> List[AlertRule]:
        """Initialize default alert rules"""
        return [
            AlertRule(
                rule_id="critical_risk",
                name="Critical Fire Risk",
                condition="risk_score >= 75",
                priority=AlertPriority.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, 
                         NotificationChannel.PUSH, NotificationChannel.SIREN,
                         NotificationChannel.DASHBOARD],
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="high_risk",
                name="High Fire Risk",
                condition="risk_score >= 60",
                priority=AlertPriority.HIGH,
                channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH,
                         NotificationChannel.DASHBOARD],
                cooldown_minutes=15
            ),
            AlertRule(
                rule_id="smoke_detected",
                name="Smoke Detection",
                condition="smoke_level > 2500",
                priority=AlertPriority.HIGH,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS,
                         NotificationChannel.DASHBOARD],
                cooldown_minutes=10
            ),
            AlertRule(
                rule_id="rapid_temp_rise",
                name="Rapid Temperature Increase",
                condition="temp_change_rate > 5",
                priority=AlertPriority.MEDIUM,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown_minutes=20
            ),
            AlertRule(
                rule_id="sensor_offline",
                name="Sensor Node Offline",
                condition="node_offline == True",
                priority=AlertPriority.MEDIUM,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown_minutes=30
            ),
            AlertRule(
                rule_id="sprinkler_activated",
                name="Sprinkler System Activated",
                condition="sprinkler_status == 'on'",
                priority=AlertPriority.HIGH,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS,
                         NotificationChannel.DASHBOARD],
                cooldown_minutes=0  # Always alert
            ),
            AlertRule(
                rule_id="nearby_fire_hotspot",
                name="Nearby Fire Hotspot Detected",
                condition="hotspot_distance < 10",
                priority=AlertPriority.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS,
                         NotificationChannel.PUSH, NotificationChannel.DASHBOARD],
                cooldown_minutes=60
            )
        ]
    
    async def evaluate_rules(self, sensor_data: Dict) -> List[AlertMessage]:
        """
        Evaluate all alert rules against current data
        """
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule.rule_id in self.last_alert_time:
                time_since_last = datetime.utcnow() - self.last_alert_time[rule.rule_id]
                if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                    continue
            
            # Evaluate condition
            if self._evaluate_condition(rule.condition, sensor_data):
                alert = await self._create_alert(rule, sensor_data)
                triggered_alerts.append(alert)
                self.last_alert_time[rule.rule_id] = datetime.utcnow()
        
        return triggered_alerts
    
    def _evaluate_condition(self, condition: str, data: Dict) -> bool:
        """
        Safely evaluate alert condition
        """
        try:
            # Create safe evaluation context
            context = {
                'risk_score': data.get('fire_risk_score', 0),
                'temperature': data.get('temperature', 0),
                'humidity': data.get('humidity', 0),
                'smoke_level': data.get('smoke_level', 0),
                'rain_level': data.get('rain_level', 0),
                'temp_change_rate': data.get('temp_change_rate', 0),
                'node_offline': data.get('node_offline', False),
                'sprinkler_status': data.get('sprinkler_status', 'off'),
                'hotspot_distance': data.get('hotspot_distance', 999),
            }
            
            # Safely evaluate
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            print(f"⚠️ Error evaluating condition '{condition}': {e}")
            return False
    
    async def _create_alert(self, rule: AlertRule, data: Dict) -> AlertMessage:
        """Create alert message from triggered rule"""
        import uuid
        
        alert_id = f"ALERT-{uuid.uuid4().hex[:8]}"
        
        # Generate contextual message
        message = self._generate_alert_message(rule, data)
        
        alert = AlertMessage(
            alert_id=alert_id,
            title=rule.name,
            message=message,
            priority=rule.priority,
            source="smart_alert_system",
            data=data,
            channels=rule.channels,
            timestamp=datetime.utcnow()
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        return alert
    
    def _generate_alert_message(self, rule: AlertRule, data: Dict) -> str:
        """Generate human-readable alert message"""
        messages = {
            "critical_risk": f"CRITICAL FIRE RISK DETECTED! Risk Score: {data.get('fire_risk_score', 0):.1f}%. "
                           f"Temperature: {data.get('temperature', 0):.1f}°C, "
                           f"Humidity: {data.get('humidity', 0):.1f}%, "
                           f"Smoke: {data.get('smoke_level', 0):.0f}. "
                           f"IMMEDIATE ACTION REQUIRED!",
            
            "high_risk": f"High fire risk detected. Risk Score: {data.get('fire_risk_score', 0):.1f}%. "
                        f"Conditions: Temp {data.get('temperature', 0):.1f}°C, "
                        f"Humidity {data.get('humidity', 0):.1f}%. Monitor closely.",
            
            "smoke_detected": f"SMOKE DETECTED! Level: {data.get('smoke_level', 0):.0f}. "
                            f"Location: Zone {data.get('zone_id', 'Unknown')}. "
                            f"Investigate immediately!",
            
            "rapid_temp_rise": f"Rapid temperature increase detected: "
                             f"+{data.get('temp_change_rate', 0):.1f}°C in recent period. "
                             f"Current: {data.get('temperature', 0):.1f}°C",
            
            "sensor_offline": f"Sensor node '{data.get('node_id', 'Unknown')}' is offline. "
                            f"Last seen: {data.get('last_heartbeat', 'Unknown')}",
            
            "sprinkler_activated": f"Sprinkler system ACTIVATED in zone {data.get('zone_id', 'Unknown')}. "
                                 f"Reason: {data.get('activation_reason', 'Automatic fire suppression')}",
            
            "nearby_fire_hotspot": f"SATELLITE FIRE HOTSPOT DETECTED {data.get('hotspot_distance', 0):.1f}km away! "
                                 f"Confidence: {data.get('hotspot_confidence', 0)}%. "
                                 f"Increase monitoring immediately!"
        }
        
        return messages.get(rule.rule_id, f"Alert triggered: {rule.name}")
    
    async def _send_notifications(self, alert: AlertMessage):
        """Send alert through specified channels"""
        tasks = []
        
        for channel in alert.channels:
            if channel == NotificationChannel.EMAIL:
                tasks.append(self._send_email(alert))
            elif channel == NotificationChannel.SMS:
                tasks.append(self._send_sms(alert))
            elif channel == NotificationChannel.PUSH:
                tasks.append(self._send_push_notification(alert))
            elif channel == NotificationChannel.WEBHOOK:
                tasks.append(self._send_webhook(alert))
            elif channel == NotificationChannel.SIREN:
                tasks.append(self._activate_siren(alert))
            # DASHBOARD is handled by WebSocket in main application
        
        # Execute all notifications in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_email(self, alert: AlertMessage):
        """Send email notification"""
        if not self.smtp_username or not self.email_recipients:
            print("⚠️ Email not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.email_recipients)
            msg['Subject'] = f"[{alert.priority.value.upper()}] {alert.title}"
            
            # Create email body
            body = f"""
            <html>
            <body>
                <h2 style="color: {'red' if alert.priority == AlertPriority.CRITICAL else 'orange'};">
                    {alert.title}
                </h2>
                <p><strong>Priority:</strong> {alert.priority.value.upper()}</p>
                <p><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                
                <h3>Details:</h3>
                <p>{alert.message}</p>
                
                <h3>Sensor Data:</h3>
                <ul>
                    <li>Temperature: {alert.data.get('temperature', 'N/A')}°C</li>
                    <li>Humidity: {alert.data.get('humidity', 'N/A')}%</li>
                    <li>Smoke Level: {alert.data.get('smoke_level', 'N/A')}</li>
                    <li>Fire Risk Score: {alert.data.get('fire_risk_score', 'N/A')}%</li>
                </ul>
                
                <p style="color: red; font-weight: bold;">
                    This is an automated alert from the Smart Forest Fire Prevention System.
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent for alert {alert.alert_id}")
        
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    async def _send_sms(self, alert: AlertMessage):
        """
        Send SMS notification (via Twilio or similar)
        Placeholder implementation
        """
        print(f"📱 SMS: [{alert.priority.value.upper()}] {alert.title}")
        # In production, integrate with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"[{alert.priority.value.upper()}] {alert.title}: {alert.message[:100]}",
        #     from_=twilio_number,
        #     to=recipient_number
        # )
    
    async def _send_push_notification(self, alert: AlertMessage):
        """
        Send push notification
        Placeholder implementation
        """
        print(f"🔔 Push: {alert.title}")
        # In production, integrate with Firebase Cloud Messaging or similar
    
    async def _send_webhook(self, alert: AlertMessage):
        """Send webhook notification"""
        import aiohttp
        
        for url in self.webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        'alert_id': alert.alert_id,
                        'title': alert.title,
                        'message': alert.message,
                        'priority': alert.priority.value,
                        'timestamp': alert.timestamp.isoformat(),
                        'data': alert.data
                    }
                    
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            print(f"✅ Webhook sent to {url}")
                        else:
                            print(f"⚠️ Webhook failed: {response.status}")
            
            except Exception as e:
                print(f"❌ Webhook error: {e}")
    
    async def _activate_siren(self, alert: AlertMessage):
        """
        Activate physical siren/alarm
        Placeholder - would control GPIO or relay
        """
        if alert.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH]:
            print(f"🚨 SIREN ACTIVATED: {alert.title}")
            # In production, control GPIO pin or send command to hardware
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            print(f"✅ Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Mark an alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            del self.active_alerts[alert_id]
            print(f"✅ Alert {alert_id} resolved by {resolved_by}")
            return True
        return False
    
    def get_active_alerts(self, priority: Optional[AlertPriority] = None) -> List[AlertMessage]:
        """Get all active alerts, optionally filtered by priority"""
        alerts = list(self.active_alerts.values())
        
        if priority:
            alerts = [a for a in alerts if a.priority == priority]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        total_alerts = len(self.alert_history)
        active_count = len(self.active_alerts)
        
        # Count by priority
        priority_counts = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        
        for alert in self.alert_history:
            priority_counts[alert.priority.value] += 1
        
        # Calculate average response time (mock data for now)
        avg_acknowledgment_time = 5.2  # minutes
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_count,
            'resolved_alerts': total_alerts - active_count,
            'by_priority': priority_counts,
            'avg_acknowledgment_time_minutes': avg_acknowledgment_time,
            'last_24h': len([a for a in self.alert_history 
                           if (datetime.utcnow() - a.timestamp).days < 1])
        }


# Global alert system instance
alert_system = SmartAlertSystem()
