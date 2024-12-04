from flask import Flask, jsonify
from kafka import KafkaConsumer
import logging
import threading
import json
from datetime import datetime

# Flask App
app = Flask(__name__)

# Kafka Configurations
KAFKA_BROKER = 'kafka-test.kafka.svc.cluster.local:9092' 
TOPIC_NAME = 'health_checks_topic'

# Initialize Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('HealthCheckService')

# Store health check results
health_statuses = []

# Kafka Consumer Function
def consume_health_checks():
    global health_statuses
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='health_check_group',
        auto_offset_reset='earliest'
    )
    logger.info(f"Started Kafka consumer on topic '{TOPIC_NAME}'")

    for message in consumer:
        health_check = message.value
        logger.info(f"Received health check: {health_check}")
        health_statuses.append(health_check)

# Background Thread to Consume Kafka Messages
def start_kafka_consumer():
    thread = threading.Thread(target=consume_health_checks, daemon=True)
    thread.start()

# REST API Endpoint
@app.route('/check_health', methods=['GET'])
def check_health():
    """
    Retrieve health status of microservices.
    """
    if not health_statuses:
        return jsonify({'message': 'No health checks received yet.'}), 200
    
    # Return latest statuses for simplicity
    return jsonify({
        'message': f'{len(health_statuses)} health checks retrieved.',
        'statuses': health_statuses
    }), 200

if __name__ == '__main__':
    logger.info("Starting HealthCheckService...")
    start_kafka_consumer()  # Start Kafka consumer in a separate thread
    app.run(host='0.0.0.0', port=5000)