from flask import Flask, jsonify
from kafka import KafkaConsumer
import threading
import logging
import json
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Kafka configuration
KAFKA_BROKER = 'kafka-test.kafka.svc.cluster.local:9092' 
TOPIC_NAME = 'health_checks_topic'

# Global variable to store the latest health check status
latest_health_check = {}

# Function to consume messages from Kafka
def consume_health_checks():
    global latest_health_check
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        logging.info("Connected to Kafka broker and listening for messages...")
        for message in consumer:
            health_data = message.value
            logging.info(f"Received health check: {health_data}")
            # Update the latest health check
            latest_health_check = health_data
    except Exception as e:
        logging.error(f"Error consuming Kafka messages: {e}")

# REST API endpoint to fetch the latest health status
@app.route('/get_latest_health_check', methods=['GET'])
def get_latest_health_check():
    if not latest_health_check:
        return jsonify({"error": "No health check data available"}), 404
    return jsonify(latest_health_check)

# Start the Kafka consumer in a separate thread
threading.Thread(target=consume_health_checks, daemon=True).start()

# Start Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)