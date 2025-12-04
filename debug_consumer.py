from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'game_telemetry', # The topic we want to spy on
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest', # Start from the beginning
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🕵️ Listening to 'game_telemetry' topic...")

try:
    for message in consumer:
        event = message.value
        # Print only the important parts to keep it readable
        print(f"RECEIVED: Player {event['player_id']} | Type: {'CHEAT' if event.get('label') == 1 else 'LEGIT'}")
except KeyboardInterrupt:
    print("Stopped.")