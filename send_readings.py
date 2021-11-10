import json
import random
import time

from app.logger import get_logger
from app.sensor_queue import get_mqtt_client
from app.config import base_temperature, temperature_readings_topic, sensor_data_update_frequency

logger = get_logger("mock-sensors")


def send_readings():
    client_id = "python-writer-client"
    client = get_mqtt_client(client_id)
    topic = temperature_readings_topic
    logger.info(f"Starting process to send sensor readings to queue for topic {topic}")

    while True:

        for i in range(1, 4):
            action = random.choice(["+", "-"])
            value_diff = random.choice(range(1, 20))

            value = base_temperature
            if action == "+":
                value += value * value_diff / 100
            elif action == "-":
                value -= value * value_diff / 100

            message = {
                "sensorID": f"sensor-{i}",
                "type": "temperature",
                "value": value
            }

            result = client.publish(topic, json.dumps(message))

            status = result[0]
            if status == 0:
                logger.info(f"Send `{message}` to topic `{topic}`")
            else:
                logger.error(f"Failed to send message to topic {topic}")

        time.sleep(sensor_data_update_frequency)


if __name__ == "__main__":
    logger.info("Starting process to send sensor readings...")

    send_readings()
