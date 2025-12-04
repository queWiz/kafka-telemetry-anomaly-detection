import json
import joblib
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import pandas as pd

# Configuration
KAFKA_BROKER = "localhost:9092"
SOURCE_TOPIC = "game_telemetry"
ALERTS_TOPIC = "cheat_flags"

# 1. Load the Trained Model
print("🧠 Loading AI Model...")
model = joblib.load('cheat_detector_model.pkl')

# 2. Setup Kafka Connections
consumer = KafkaConsumer(
    SOURCE_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"👀 Detector listening on '{SOURCE_TOPIC}'...")

for message in consumer:
    event = message.value
    
    # Extract the features the model expects: [reaction_time, mouse_speed, accuracy]
    # Note: We must match the order we used in training!
    features = [
        event['telemetry']['reaction_time_ms'],
        event['telemetry']['mouse_speed'],
        event['telemetry']['accuracy_rating']
    ]
    
    # Reshape for Scikit-Learn (it expects a list of lists)
    # features_array = np.array([features])
    features_df = pd.DataFrame([features], columns=['reaction_time', 'mouse_speed', 'accuracy'])
    
    # 3. Predict
    # Result is 1 (Normal) or -1 (Anomaly)
    prediction = model.predict(features_df)[0]
    
    if prediction == -1:
        print(f"🚨 ANOMALY DETECTED: Player {event['player_id']}")
        
        # 4. Create Alert Object
        alert = {
            "match_id": event['match_id'],
            "player_id": event['player_id'],
            "reason": "Statistical Anomaly (Aimbot Behavior)",
            "telemetry_snapshot": event['telemetry'],
            "timestamp": event['timestamp']
        }
        
        # 5. Push to Alerts Topic
        producer.send(ALERTS_TOPIC, alert)
        print(f"   -> Alert sent to '{ALERTS_TOPIC}'")