import time
import json
import random
import uuid
from kafka import KafkaProducer

# --- CONFIGURATION ---
KAFKA_TOPIC = "game_telemetry"
KAFKA_SERVER = "localhost:9092"

# 1. Setup Kafka Producer (With Retry Logic)
producer = None
while producer is None:
    try:
        print(f"⏳ Attempting to connect to Kafka at {KAFKA_SERVER}...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("✅ Connected to Kafka!")
    except Exception as e:
        print("❌ Connection failed. Kafka might be starting up. Retrying in 3 seconds...")
        time.sleep(3)

# 2. Define our "Players"
# We simulate a 5v5 match, but let's just track 5 players for now.
# One of them (player_3) will turn on their hacks later.
PLAYERS = [
    {"id": "player_1", "role": "legit", "skill": "noob"},
    {"id": "player_2", "role": "legit", "skill": "pro"},
    {"id": "player_3", "role": "cheater", "active_hacks": False}, # Starts clean
    {"id": "player_4", "role": "legit", "skill": "average"},
    {"id": "player_5", "role": "legit", "skill": "average"},
]

MATCH_ID = str(uuid.uuid4())[:8]

def generate_legit_action(player):
    """Simulates normal human behavior."""
    # Humans are slower and less accurate
    reaction_time = random.randint(150, 600)  # ms
    mouse_speed = random.randint(5, 20)       # pixels per tick (variable)
    
    # Pros are faster, noobs are slower
    if player.get("skill") == "pro":
        reaction_time -= 50
    
    return {
        "player_id": player["id"],
        "match_id": MATCH_ID,
        "event_type": "shoot",
        "timestamp": time.time(),
        "telemetry": {
            "reaction_time_ms": reaction_time,
            "mouse_speed": mouse_speed,
            "accuracy_rating": round(random.uniform(0.2, 0.8), 2), # 20-80% accuracy
            "headshot": random.choice([True, False, False, False]) # 25% HS rate
        },
        "label": 0 # 0 = Legit (for training if needed)
    }

def generate_cheater_action(player):
    """Simulates Aimbot behavior."""
    # Aimbots are instant and perfect
    reaction_time = random.randint(10, 80)    # Inhumanly fast (<100ms)
    mouse_speed = random.randint(50, 100)     # Snaps to target instantly
    
    return {
        "player_id": player["id"],
        "match_id": MATCH_ID,
        "event_type": "shoot",
        "timestamp": time.time(),
        "telemetry": {
            "reaction_time_ms": reaction_time,
            "mouse_speed": mouse_speed,
            "accuracy_rating": round(random.uniform(0.95, 1.0), 2), # 95-100% accuracy
            "headshot": True # Aimbot usually locks head
        },
        "label": 1 # 1 = Cheat
    }

print(f"🎮 Starting Match {MATCH_ID}...")
print("Press Ctrl+C to stop.")

try:
    while True:
        # Every 0.1 to 0.5 seconds, a random event happens
        time.sleep(random.uniform(0.1, 0.5))
        
        # Pick a random player to do something
        player = random.choice(PLAYERS)
        
        # Logic: If it's the Cheater, decide if they toggle hacks
        # (Cheaters try to hide it, so they don't cheat 100% of the time)
        if player["role"] == "cheater":
            # 30% chance they toggle the aimbot on for this shot
            is_hacking = random.random() < 0.3 
            if is_hacking:
                data = generate_cheater_action(player)
                print(f"⚠️ [CHEAT EVENT] {player['id']} | React: {data['telemetry']['reaction_time_ms']}ms | Acc: {data['telemetry']['accuracy_rating']}")
            else:
                data = generate_legit_action(player) # Acting normal
                print(f"   [Normal]      {player['id']} | React: {data['telemetry']['reaction_time_ms']}ms")
        else:
            data = generate_legit_action(player)
            print(f"   [Normal]      {player['id']} | React: {data['telemetry']['reaction_time_ms']}ms")

        # 3. Send to Kafka
        producer.send(KAFKA_TOPIC, data)

except KeyboardInterrupt:
    print("\n🛑 Game Over.")
    producer.close()