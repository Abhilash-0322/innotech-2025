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
from config import settings
from database import get_database


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
        
        # Email configuration from settings
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = "forest-fire-alert@system.com"
        
        # SMS/Twilio configuration from settings
        self.twilio_account_sid = settings.twilio_account_sid
        self.twilio_auth_token = settings.twilio_auth_token
        self.twilio_phone_number = settings.twilio_phone_number
        
        # Parse recipient lists from comma-separated strings
        self.email_recipients = [e.strip() for e in settings.email_recipients.split(',') if e.strip()]
        self.sms_recipients = [s.strip() for s in settings.sms_recipients.split(',') if s.strip()]
        self.webhook_urls = []
        
        # Get SMS thresholds from settings
        self.sms_risk_threshold = settings.sms_risk_threshold
        self.sms_smoke_threshold = settings.sms_smoke_threshold
        
        print(f"📧 Email recipients configured: {len(self.email_recipients)}")
        print(f"📱 SMS recipients configured: {len(self.sms_recipients)}")
        print(f"🔥 SMS risk threshold: {self.sms_risk_threshold}%")
        print(f"💨 SMS smoke threshold: {self.sms_smoke_threshold}")
    
    def _init_default_rules(self) -> List[AlertRule]:
        """Initialize default alert rules"""
        return [
            AlertRule(
                rule_id="critical_risk",
                name="Critical Fire Risk",
                condition=f"risk_score >= {settings.sms_risk_threshold}",
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
                condition=f"smoke_level >= {settings.sms_smoke_threshold}",
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
        
        print(f"\n🔍 Evaluating {len(self.alert_rules)} alert rules...")
        print(f"   Sensor data: risk_score={sensor_data.get('fire_risk_score', 0)}, "
              f"temp={sensor_data.get('temperature', 0)}, "
              f"smoke={sensor_data.get('smoke_level', 0)}")
        
        for rule in self.alert_rules:
            if not rule.enabled:
                print(f"   ⏭️  Rule '{rule.name}' is disabled, skipping")
                continue
            
            # Check cooldown
            if rule.rule_id in self.last_alert_time:
                time_since_last = datetime.utcnow() - self.last_alert_time[rule.rule_id]
                if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                    remaining = rule.cooldown_minutes * 60 - time_since_last.total_seconds()
                    print(f"   ⏱️  Rule '{rule.name}' in cooldown ({remaining:.0f}s remaining)")
                    continue
            
            # Evaluate condition
            print(f"   📋 Evaluating rule '{rule.name}': {rule.condition}")
            if self._evaluate_condition(rule.condition, sensor_data):
                print(f"   ✅ Rule '{rule.name}' TRIGGERED!")
                alert = await self._create_alert(rule, sensor_data)
                triggered_alerts.append(alert)
                self.last_alert_time[rule.rule_id] = datetime.utcnow()
            else:
                print(f"   ❌ Rule '{rule.name}' not triggered")
        
        print(f"📊 Total alerts triggered: {len(triggered_alerts)}\n")
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
        Send SMS notification via Twilio with recent sensor history
        """
        print(f"\n📱 Attempting to send SMS for alert: {alert.alert_id}")
        print(f"   Priority: {alert.priority.value}")
        print(f"   Title: {alert.title}")
        
        if not self.twilio_account_sid or not self.twilio_auth_token or not self.twilio_phone_number:
            print("⚠️ SMS not configured: Missing Twilio credentials")
            print(f"   Account SID: {'✓' if self.twilio_account_sid else '✗'}")
            print(f"   Auth Token: {'✓' if self.twilio_auth_token else '✗'}")
            print(f"   Phone Number: {'✓' if self.twilio_phone_number else '✗'}")
            return
        
        if not self.sms_recipients:
            print("⚠️ No SMS recipients configured")
            return
        
        print(f"   Recipients: {len(self.sms_recipients)} - {self.sms_recipients}")
        
        try:
            from twilio.rest import Client
            
            # Initialize Twilio client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Fetch recent sensor history
            history = await self._fetch_recent_sensor_history(limit=3)
            
            # Create short SMS message (SMS has 160 char limit for best compatibility)
            priority_emoji = {
                AlertPriority.LOW: "ℹ️",
                AlertPriority.MEDIUM: "⚠️",
                AlertPriority.HIGH: "🔥",
                AlertPriority.CRITICAL: "🚨"
            }
            
            emoji = priority_emoji.get(alert.priority, "⚠️")
            
            # Current values
            risk_score = alert.data.get('fire_risk_score', 0)
            temp = alert.data.get('temperature', 0)
            smoke = alert.data.get('smoke_level', 0)
            
            # Build SMS with historical trend
            sms_body = (
                f"{emoji} FIRE ALERT: {alert.title}\n"
                f"CURRENT: Risk:{risk_score:.0f}% Temp:{temp:.1f}°C Smoke:{smoke:.0f}\n"
            )
            
            # Add trend data if available
            if history and len(history) >= 2:
                # Show last 2-3 readings for trend
                sms_body += "TREND:\n"
                for i, reading in enumerate(history[:3], 1):
                    ts = reading.get('timestamp', datetime.utcnow())
                    if isinstance(ts, datetime):
                        time_str = ts.strftime('%H:%M')
                    else:
                        time_str = "??:??"
                    
                    r = reading.get('fire_risk_score', 0)
                    s = reading.get('smoke_level', 0)
                    sms_body += f"{time_str} R:{r:.0f}% S:{s:.0f}\n"
            
            sms_body += f"Time: {alert.timestamp.strftime('%H:%M:%S')}"
            
            print(f"📝 SMS Body ({len(sms_body)} chars):\n{sms_body}")
            
            # Send to all recipients
            sent_count = 0
            failed_count = 0
            
            for recipient in self.sms_recipients:
                try:
                    message = client.messages.create(
                        body=sms_body,
                        from_=self.twilio_phone_number,
                        to=recipient
                    )
                    
                    if message.sid:
                        print(f"✅ SMS sent to {recipient} (SID: {message.sid})")
                        sent_count += 1
                    else:
                        print(f"⚠️ SMS failed for {recipient}")
                        failed_count += 1
                        
                except Exception as recipient_error:
                    print(f"❌ Failed to send SMS to {recipient}: {recipient_error}")
                    failed_count += 1
            
            print(f"📱 SMS Alert Summary: {sent_count} sent, {failed_count} failed")
        
        except ImportError:
            print("❌ Twilio library not installed. Run: pip install twilio")
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")
    
    async def _fetch_recent_sensor_history(self, limit: int = 3) -> List[Dict]:
        """
        Fetch recent sensor readings from database
        Returns list of recent sensor data for trend analysis
        """
        try:
            db = get_database()
            if db is None:
                print("⚠️ Database not available for historical data")
                return []
            
            # Fetch most recent readings
            cursor = db.sensor_data.find().sort("timestamp", -1).limit(limit)
            history = []
            
            async for doc in cursor:
                history.append({
                    'timestamp': doc.get('timestamp'),
                    'temperature': doc.get('temperature', 0),
                    'smoke_level': doc.get('smoke_level', 0),
                    'fire_risk_score': doc.get('fire_risk_score', 0),
                    'humidity': doc.get('humidity', 0)
                })
            
            print(f"📊 Fetched {len(history)} recent sensor readings")
            return history
            
        except Exception as e:
            print(f"❌ Error fetching sensor history: {e}")
            return []
    
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
