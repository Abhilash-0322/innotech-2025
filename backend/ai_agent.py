"""
Agentic AI Module for Fire Risk Assessment
Uses Groq API for fast, intelligent fire risk analysis
"""
from typing import Dict, List, Optional
import json
from datetime import datetime
from groq import Groq
from models import SensorData, FireRiskAnalysis, RiskLevel
from config import settings


class FireRiskAgent:
    """Agentic AI for analyzing fire risk and making decisions"""
    
    def __init__(self):
        self.client = None
        if settings.groq_api_key:
            self.client = Groq(api_key=settings.groq_api_key)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        return f"""You are an expert AI agent for forest fire risk assessment and prevention.

Your role is to analyze real-time sensor data from an IoT system and make intelligent decisions about fire risk.

You have access to the following sensors:
1. DHT22 Temperature Sensor (°C)
2. DHT22 Humidity Sensor (%)
3. MQ-2 Smoke/Gas Sensor (0-4095 scale, higher = more smoke)
4. Rain Sensor (0-4095 scale, higher = less rain)

Your tasks:
1. Analyze the sensor readings
2. Calculate a fire risk score (0-100)
3. Determine risk level (low, medium, high, critical)
4. Provide clear reasoning for your assessment
5. Give specific recommendations
6. Decide if sprinklers should be activated
7. Provide confidence level in your assessment

Risk Level Guidelines:
- LOW (0-25): Safe conditions, normal monitoring
- MEDIUM (26-50): Elevated risk, increase monitoring
- HIGH (51-75): Dangerous conditions, prepare for action
- CRITICAL (76-100): Immediate danger, activate sprinklers

Key Risk Factors:
- High temperature (>{settings.high_temp_threshold}°C)
- Low humidity (<{settings.low_humidity_threshold}%)
- High smoke levels (>{settings.high_smoke_threshold})
- No rain (dry conditions)
- Combinations of the above

Decision Making:
- Be conservative with fire risk
- Consider environmental context
- Balance false alarms with safety
- Activate sprinklers at CRITICAL level or HIGH with smoke
- Provide actionable recommendations

Respond ONLY with valid JSON in this exact format:
{{
    "risk_score": <float 0-100>,
    "risk_level": "<low|medium|high|critical>",
    "reasoning": "<clear explanation>",
    "recommendations": ["<recommendation1>", "<recommendation2>", ...],
    "should_activate_sprinkler": <boolean>,
    "confidence": <float 0-1>
}}
"""
    
    async def analyze_fire_risk(self, sensor_data: SensorData) -> FireRiskAnalysis:
        """
        Analyze sensor data using AI agent and return fire risk assessment
        """
        # If no AI client, use rule-based fallback
        if not self.client:
            return self._rule_based_analysis(sensor_data)
        
        try:
            # Prepare the sensor data for the AI
            user_message = f"""Analyze the following real-time sensor data:

Temperature: {sensor_data.temperature}°C
Humidity: {sensor_data.humidity}%
Smoke Level: {sensor_data.smoke_level} (0-4095 scale)
Rain Level: {sensor_data.rain_level} (0-4095 scale, higher = drier)
Rain Detected: {sensor_data.rain_detected}
Timestamp: {sensor_data.timestamp.isoformat()}

Provide your fire risk assessment."""

            # Call Groq API (synchronous)
            response = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=500
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            analysis_data = json.loads(ai_response)
            
            # Create FireRiskAnalysis object
            analysis = FireRiskAnalysis(
                risk_score=analysis_data["risk_score"],
                risk_level=RiskLevel(analysis_data["risk_level"]),
                reasoning=analysis_data["reasoning"],
                recommendations=analysis_data["recommendations"],
                should_activate_sprinkler=analysis_data["should_activate_sprinkler"],
                confidence=analysis_data["confidence"],
                timestamp=datetime.utcnow()
            )
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}. Falling back to rule-based.")
            return self._rule_based_analysis(sensor_data)
    
    def _rule_based_analysis(self, sensor_data: SensorData) -> FireRiskAnalysis:
        """
        Fallback rule-based analysis when AI is not available
        """
        risk_score = 0.0
        risk_factors = []
        recommendations = []
        
        # Temperature factor
        if sensor_data.temperature > settings.high_temp_threshold:
            temp_factor = min((sensor_data.temperature - 20) * 2, 35)
            risk_score += temp_factor
            risk_factors.append(f"High temperature: {sensor_data.temperature}°C")
            recommendations.append("Monitor temperature closely")
        
        # Humidity factor (inverse relationship)
        if sensor_data.humidity < settings.low_humidity_threshold:
            humidity_factor = min((settings.low_humidity_threshold - sensor_data.humidity) * 1.5, 30)
            risk_score += humidity_factor
            risk_factors.append(f"Low humidity: {sensor_data.humidity}%")
            recommendations.append("Low humidity increases fire risk")
        
        # Smoke factor
        if sensor_data.smoke_level > settings.high_smoke_threshold:
            smoke_factor = min((sensor_data.smoke_level / 40), 35)
            risk_score += smoke_factor
            risk_factors.append(f"Smoke detected: {sensor_data.smoke_level}")
            recommendations.append("⚠️ SMOKE DETECTED - Investigate immediately")
        elif sensor_data.smoke_level > 50:
            risk_score += 10
            risk_factors.append("Elevated smoke levels")
            recommendations.append("Increased smoke monitoring advised")
        
        # Rain factor (dry conditions)
        if sensor_data.rain_level > 4000 and not sensor_data.rain_detected:
            risk_score += 10
            risk_factors.append("Dry conditions (no rain)")
            recommendations.append("Dry conditions increase fire risk")
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 76:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 51:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 26:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Sprinkler activation logic
        should_activate = (
            risk_level == RiskLevel.CRITICAL or
            (risk_level == RiskLevel.HIGH and sensor_data.smoke_level > settings.high_smoke_threshold)
        )
        
        # Build reasoning
        reasoning = f"Fire risk score: {risk_score:.1f}/100. "
        if risk_factors:
            reasoning += "Risk factors: " + ", ".join(risk_factors)
        else:
            reasoning += "Normal conditions detected."
        
        # Default recommendations
        if not recommendations:
            recommendations = ["Continue normal monitoring"]
        
        if should_activate:
            recommendations.insert(0, "🚨 ACTIVATE SPRINKLERS IMMEDIATELY")
        
        return FireRiskAnalysis(
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            reasoning=reasoning,
            recommendations=recommendations,
            should_activate_sprinkler=should_activate,
            confidence=0.85,  # Rule-based has fixed confidence
            timestamp=datetime.utcnow()
        )
    
    async def get_contextual_advice(self, sensor_history: List[Dict]) -> str:
        """
        Get contextual advice based on sensor history trends
        """
        if not self.client or not sensor_history:
            return "Insufficient data for contextual analysis."
        
        try:
            history_summary = "\n".join([
                f"Time: {data['timestamp']}, Temp: {data['temperature']}°C, "
                f"Humidity: {data['humidity']}%, Smoke: {data['smoke_level']}"
                for data in sensor_history[-10:]  # Last 10 readings
            ])
            
            prompt = f"""Based on the following recent sensor history, provide brief actionable advice:

{history_summary}

Give 2-3 short recommendations based on trends you observe."""

            response = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You are a fire prevention advisor. Give brief, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Contextual advice failed: {e}")
            return "Unable to generate contextual advice at this time."


# Global agent instance
fire_risk_agent = FireRiskAgent()
