"""
Machine Learning Fire Weather Index (FWI) Predictor
Uses historical data to predict fire risk 1-24 hours ahead
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class FireWeatherIndexPredictor:
    """
    ML-based Fire Weather Index predictor
    Trains on historical sensor data to predict future fire risk
    """
    
    def __init__(self, model_path: str = "models/fwi_model.pkl"):
        self.model_path = Path(model_path)
        self.regression_model = None
        self.classification_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'temperature', 'humidity', 'smoke_level', 'rain_level',
            'hour_of_day', 'day_of_week', 'month',
            'temp_change_rate', 'humidity_change_rate',
            'temp_ma_1h', 'humidity_ma_1h',  # Moving averages
            'temp_std_1h', 'smoke_max_1h'
        ]
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.regression_model = data['regression']
                self.classification_model = data['classification']
                self.scaler = data['scaler']
                self.is_trained = True
                print("✅ FWI model loaded successfully")
            except Exception as e:
                print(f"⚠️ Failed to load model: {e}")
    
    def _save_model(self):
        """Save trained model"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'regression': self.regression_model,
            'classification': self.classification_model,
            'scaler': self.scaler
        }, self.model_path)
        print("✅ FWI model saved successfully")
    
    def _extract_features(self, sensor_history: List[Dict]) -> np.ndarray:
        """
        Extract features from sensor history
        Includes temporal features and rolling statistics
        """
        if len(sensor_history) == 0:
            return np.array([])
        
        features = []
        for i, data in enumerate(sensor_history):
            timestamp = data.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Basic features
            feature_dict = {
                'temperature': data.get('temperature', 0),
                'humidity': data.get('humidity', 0),
                'smoke_level': data.get('smoke_level', 0),
                'rain_level': data.get('rain_level', 0),
                'hour_of_day': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'month': timestamp.month,
            }
            
            # Calculate change rates (if we have previous data)
            if i > 0:
                prev = sensor_history[i-1]
                feature_dict['temp_change_rate'] = data.get('temperature', 0) - prev.get('temperature', 0)
                feature_dict['humidity_change_rate'] = data.get('humidity', 0) - prev.get('humidity', 0)
            else:
                feature_dict['temp_change_rate'] = 0
                feature_dict['humidity_change_rate'] = 0
            
            # Calculate rolling statistics (last hour - assuming 1 reading per minute)
            lookback = min(i + 1, 60)
            recent_data = sensor_history[max(0, i-lookback+1):i+1]
            
            temps = [d.get('temperature', 0) for d in recent_data]
            humids = [d.get('humidity', 0) for d in recent_data]
            smokes = [d.get('smoke_level', 0) for d in recent_data]
            
            feature_dict['temp_ma_1h'] = np.mean(temps)
            feature_dict['humidity_ma_1h'] = np.mean(humids)
            feature_dict['temp_std_1h'] = np.std(temps)
            feature_dict['smoke_max_1h'] = np.max(smokes)
            
            features.append([feature_dict[col] for col in self.feature_columns])
        
        return np.array(features)
    
    def train(self, sensor_history: List[Dict], risk_scores: List[float], risk_levels: List[str]):
        """
        Train the FWI prediction models
        
        Args:
            sensor_history: List of sensor readings with timestamps
            risk_scores: Corresponding fire risk scores (0-100)
            risk_levels: Corresponding risk levels (low, medium, high, critical)
        """
        if len(sensor_history) < 100:
            print("⚠️ Insufficient training data. Need at least 100 samples.")
            return False
        
        try:
            # Extract features
            X = self._extract_features(sensor_history)
            y_regression = np.array(risk_scores)
            
            # Convert risk levels to numeric
            level_map = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
            y_classification = np.array([level_map.get(level, 0) for level in risk_levels])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train regression model (for risk score prediction)
            self.regression_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            )
            self.regression_model.fit(X_scaled, y_regression)
            
            # Train classification model (for risk level prediction)
            self.classification_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.classification_model.fit(X_scaled, y_classification)
            
            self.is_trained = True
            self._save_model()
            
            # Print feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.regression_model.feature_importances_
            ))
            print("\n📊 Feature Importance:")
            for feat, imp in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {feat}: {imp:.3f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def predict(self, sensor_history: List[Dict], hours_ahead: int = 1) -> Dict:
        """
        Predict fire risk for future time periods
        
        Args:
            sensor_history: Recent sensor readings (at least last hour)
            hours_ahead: How many hours ahead to predict (1-24)
        
        Returns:
            Dict with predictions including risk_score, risk_level, confidence
        """
        if not self.is_trained:
            print("⚠️ Model not trained, returning error")
            return {
                'error': 'Model not trained yet. Please train the model first or use mock data.',
                'predictions': [],
                'is_trained': False
            }
        
        try:
            # Extract features from current data
            X = self._extract_features(sensor_history)
            if len(X) == 0:
                return {
                    'error': 'No valid sensor data',
                    'predictions': [],
                    'is_trained': self.is_trained
                }
            
            X_scaled = self.scaler.transform(X[-1:])  # Use most recent
            
            predictions = []
            
            # For simplicity, make same prediction for each hour
            # In production, you'd simulate forward in time
            for h in range(1, min(hours_ahead + 1, 25)):
                risk_score = self.regression_model.predict(X_scaled)[0]
                risk_level_idx = self.classification_model.predict(X_scaled)[0]
                confidence = np.max(self.classification_model.predict_proba(X_scaled)[0])
                
                level_map = {0: 'low', 1: 'medium', 2: 'high', 3: 'critical'}
                risk_level = level_map.get(risk_level_idx, 'medium')
                
                predictions.append({
                    'hours_ahead': h,
                    'timestamp': (datetime.utcnow() + timedelta(hours=h)).isoformat(),
                    'risk_score': float(np.clip(risk_score, 0, 100)),
                    'risk_level': risk_level,
                    'confidence': float(confidence)
                })
            
            return {
                'predictions': predictions,
                'model_version': '1.0',
                'features_used': self.feature_columns
            }
            
        except Exception as e:
            return {
                'error': f'Prediction failed: {str(e)}',
                'predictions': []
            }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if not self.is_trained:
            return {}
        
        return dict(zip(
            self.feature_columns,
            self.regression_model.feature_importances_
        ))
    
    def evaluate(self, test_data: List[Dict], test_scores: List[float]) -> Dict:
        """Evaluate model performance"""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        try:
            X = self._extract_features(test_data)
            X_scaled = self.scaler.transform(X)
            predictions = self.regression_model.predict(X_scaled)
            
            # Calculate metrics
            mae = np.mean(np.abs(predictions - test_scores))
            rmse = np.sqrt(np.mean((predictions - test_scores) ** 2))
            r2 = 1 - (np.sum((test_scores - predictions) ** 2) / 
                     np.sum((test_scores - np.mean(test_scores)) ** 2))
            
            return {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2_score': float(r2),
                'num_samples': len(test_scores)
            }
        except Exception as e:
            return {'error': str(e)}


# Global predictor instance
predictor = FireWeatherIndexPredictor()
