import json
import time

from statistics import mean

from app.config import temperature_readings_topic, valve_control_topic, base_temperature, valve_control_frequency
from app.logger import get_logger
from app.sensor_queue import get_mqtt_client


logger = get_logger("valve-control")


def compute_valve_level(temp_difference):
    """Computes the valve level based on an algorithm. The below algorithm is just a POC."""

    if temp_difference <= 1:
        return 15
    elif temp_difference <= 2:
        return 50
    elif temp_difference <= 3:
        return 75
    else:
        return 100


def set_valve_level(sensor_state, client):
    logger.info("Sending valve command action...")

    topic = valve_control_topic

    sensor_temp_values = sensor_state.values()
    if not sensor_temp_values:
        logger.info("No sensor data present")
        return

    current_temperature_avg = mean(sensor_temp_values)
    logger.info(f"Current room average temperature is: {current_temperature_avg}")

    if current_temperature_avg >= base_temperature:
        new_level = 0
    else:
        temp_difference = base_temperature - current_temperature_avg
        new_level = compute_valve_level(temp_difference)

    message = {"level": new_level}
    result = client.publish(topic, json.dumps(message))

    status = result[0]
    if status == 0:
        logger.info(f"Send `{message}` to topic `{topic}`")
    else:
        logger.error(f"Failed to send message to topic {topic}")


def control_valve():
    client_id = "python-valve-control-client"
    client = get_mqtt_client(client_id)
    topic = temperature_readings_topic
    logger.info(f"Starting process to send sensor readings to queue for topic {topic}")

    sensor_state = {}

    def on_message(client, userdata, message):
        message_payload = message.payload.decode()
        logger.info(f"Received `{message_payload}` from `{message.topic}` topic")
        message_body = json.loads(message_payload)
        sensor_state[message_body["sensorID"]] = message_body["value"]
        logger.info(f"Sensor state is: {sensor_state}")

    client.subscribe(topic)
    client.on_message = on_message

    while True:
        client.loop_read()
        set_valve_level(sensor_state, client)
        time.sleep(valve_control_frequency)


if __name__ == "__main__":
    logger.info("Starting valve control process ...")
    control_valve()
