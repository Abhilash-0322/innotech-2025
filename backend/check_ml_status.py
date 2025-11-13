"""
Check ML Model Status and Train if Needed
"""
import asyncio
from database import connect_to_mongo, close_mongo_connection, get_database
from ml_predictor import predictor

async def check_and_train():
    """Check ML model status and train if possible"""
    print("=" * 60)
    print("ML Model Status Check")
    print("=" * 60)
    
    await connect_to_mongo()
    
    try:
        db = get_database()
        
        # Check model status
        print(f"\n📊 Model Status:")
        print(f"   Is Trained: {predictor.is_trained}")
        print(f"   Model Path: {predictor.model_path}")
        print(f"   Model Exists: {predictor.model_path.exists()}")
        
        # Check available data
        sensor_count = await db.sensor_data.count_documents({})
        print(f"\n📈 Available Data:")
        print(f"   Sensor Readings: {sensor_count}")
        print(f"   Required for Training: 100")
        print(f"   Can Train: {'✅ Yes' if sensor_count >= 100 else '❌ No'}")
        
        if predictor.is_trained:
            print(f"\n✅ Model is already trained!")
            print(f"   Ready to make predictions")
            
            # Test prediction
            print(f"\n🧪 Testing prediction...")
            sensor_data = await db.sensor_data.find().sort("timestamp", -1).limit(100).to_list(100)
            
            if sensor_data:
                history = [
                    {
                        'temperature': s.get('temperature', 25),
                        'humidity': s.get('humidity', 50),
                        'smoke_level': s.get('smoke_level', 0),
                        'rain_level': s.get('rain_level', 0),
                        'timestamp': s.get('timestamp')
                    }
                    for s in sensor_data
                ]
                
                test_pred = predictor.predict(history, hours_ahead=1)
                
                if 'predictions' in test_pred and test_pred['predictions']:
                    pred = test_pred['predictions'][0]
                    print(f"   ✅ Prediction successful!")
                    print(f"   Sample (1 hour ahead):")
                    print(f"   - Risk Score: {pred['risk_score']:.1f}")
                    print(f"   - Risk Level: {pred['risk_level']}")
                    print(f"   - Confidence: {pred['confidence']*100:.1f}%")
                else:
                    print(f"   ⚠️ Prediction returned: {test_pred}")
            
        elif sensor_count >= 100:
            print(f"\n🤖 Model not trained but data is available!")
            response = input("\n   Train model now? (y/n): ")
            
            if response.lower() == 'y':
                print(f"\n🔧 Training model with {sensor_count} samples...")
                
                sensor_data = await db.sensor_data.find().sort("timestamp", -1).limit(10000).to_list(10000)
                
                sensor_history = [
                    {
                        'temperature': s.get('temperature', 25),
                        'humidity': s.get('humidity', 50),
                        'smoke_level': s.get('smoke_level', 0),
                        'rain_level': s.get('rain_level', 0),
                        'timestamp': s.get('timestamp')
                    }
                    for s in sensor_data
                ]
                
                risk_scores = [s.get('fire_risk_score', 30) for s in sensor_data]
                risk_levels = [s.get('risk_level', 'low') for s in sensor_data]
                
                success = predictor.train(sensor_history, risk_scores, risk_levels)
                
                if success:
                    print(f"\n✅ Training completed successfully!")
                else:
                    print(f"\n❌ Training failed")
            else:
                print("\n   Skipped training")
        else:
            print(f"\n⚠️ Not enough data to train model")
            print(f"   Need {100 - sensor_count} more sensor readings")
            print(f"   Keep the sensor stream running to collect data")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_and_train())
