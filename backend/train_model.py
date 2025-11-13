"""
Auto-train ML model using existing sensor data
"""
import asyncio
from database import connect_to_mongo, close_mongo_connection, get_database
from ml_predictor import predictor

async def auto_train_model():
    """Automatically train the ML model with existing data"""
    print("=" * 60)
    print("Auto-Training ML Fire Risk Predictor")
    print("=" * 60)
    
    await connect_to_mongo()
    
    try:
        db = get_database()
        
        # Get all sensor data
        print("\n📊 Fetching sensor data from database...")
        sensor_data = await db.sensor_data.find().sort("timestamp", -1).limit(10000).to_list(10000)
        
        print(f"   Found {len(sensor_data)} sensor readings")
        
        if len(sensor_data) < 100:
            print("\n⚠️ Insufficient data for training")
            print(f"   Need: 100 samples minimum")
            print(f"   Have: {len(sensor_data)} samples")
            print("\n💡 Solution: Run the sensor stream for a while to collect data")
            return False
        
        # Prepare training data
        print("\n🔧 Preparing training data...")
        sensor_history = []
        risk_scores = []
        risk_levels = []
        
        for s in sensor_data:
            sensor_history.append({
                'temperature': s.get('temperature', 25),
                'humidity': s.get('humidity', 50),
                'smoke_level': s.get('smoke_level', 0),
                'rain_level': s.get('rain_level', 0),
                'timestamp': s.get('timestamp')
            })
            risk_scores.append(s.get('fire_risk_score', 30))
            risk_levels.append(s.get('risk_level', 'low'))
        
        print(f"   Prepared {len(sensor_history)} training samples")
        
        # Train the model
        print("\n🤖 Training ML models...")
        success = predictor.train(sensor_history, risk_scores, risk_levels)
        
        if success:
            print("\n✅ Model training completed successfully!")
            print(f"   Training samples: {len(sensor_history)}")
            print(f"   Model saved to: {predictor.model_path}")
            
            # Test prediction
            print("\n🧪 Testing predictions...")
            test_prediction = predictor.predict(sensor_history[-100:], hours_ahead=6)
            
            if 'predictions' in test_prediction and test_prediction['predictions']:
                print("✅ Model can make predictions!")
                print(f"   Sample prediction for 1 hour ahead:")
                pred = test_prediction['predictions'][0]
                print(f"   - Risk Score: {pred['risk_score']:.1f}")
                print(f"   - Risk Level: {pred['risk_level']}")
                print(f"   - Confidence: {pred['confidence']*100:.1f}%")
            else:
                print("⚠️ Model trained but predictions failed")
                print(f"   Response: {test_prediction}")
            
            return True
        else:
            print("\n❌ Training failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_mongo_connection()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(auto_train_model())
