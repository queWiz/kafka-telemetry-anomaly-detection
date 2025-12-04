from kafka import KafkaProducer, KafkaConsumer
import json

# 1. Create a Producer (Sender)
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Sending test message...")
producer.send('test_topic', {'message': 'Hello from Python!'})
producer.flush()
print("Message sent!")

# 2. Create a Consumer (Receiver)
consumer = KafkaConsumer(
    'test_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening for message...")
for message in consumer:
    print(f"Received: {message.value}")
    break # Stop after receiving one message

consumer.close()