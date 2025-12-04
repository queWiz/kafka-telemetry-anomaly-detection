import json
import asyncio
from fastapi import FastAPI, WebSocket
from kafka import KafkaConsumer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS (so the frontend on port 5173 can talk to this backend on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KAFKA_BROKER = "localhost:9092"
ALERTS_TOPIC = "cheat_flags"

@app.get("/")
def health_check():
    return {"status": "running", "service": "sentinel-api"}

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    This endpoint pushes alerts to the Frontend in Real-Time.
    """
    await websocket.accept()
    print("✅ Frontend connected via WebSocket")

    # Connect to Kafka Consumer
    consumer = KafkaConsumer(
        ALERTS_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest' # Only show new alerts, not old ones
    )

    try:
        # Loop to read from Kafka and send to WebSocket
        # We use a non-blocking loop pattern here
        while True:
            # We poll Kafka manually to allow async/await to breathe
            msg_pack = consumer.poll(timeout_ms=100) 
            
            for tp, messages in msg_pack.items():
                for message in messages:
                    alert = message.value
                    # Send JSON to the Frontend
                    await websocket.send_json(alert)
                    print(f"📡 Sent alert to UI: {alert['player_id']}")
            
            # Small sleep to prevent CPU spiking
            await asyncio.sleep(0.01)
            
    except Exception as e:
        print(f"❌ WebSocket Disconnected: {e}")
    finally:
        consumer.close()