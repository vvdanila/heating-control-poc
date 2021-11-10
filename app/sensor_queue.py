from paho.mqtt import client as mqtt_client

from app.config import mqtt_broker, mqtt_port


def get_mqtt_client(client_id):
    client = mqtt_client.Client(client_id)
    client.connect(mqtt_broker, mqtt_port)
    return client
