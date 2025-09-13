import json
from aiokafka import AIOKafkaProducer
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

async def send_message(topic, message):
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        await producer.send_and_wait(topic, json.dumps(message).encode('utf-8'))
    finally:
        await producer.stop()