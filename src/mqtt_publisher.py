import json
import logging
import time
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("MQTT verbunden")
    else:
        logger.error(f"MQTT Verbindung fehlgeschlagen: {reason_code}")


def _on_disconnect(client, userdata, flags, reason_code, properties):
    logger.warning("MQTT getrennt.")


class MQTTPublisher:
    def __init__(self, broker: str, port: int, topic_prefix: str, username: str = "", password: str = ""):
        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = _on_connect
        self.client.on_disconnect = _on_disconnect

    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, class_name: str, payload: dict):
        topic = f"{self.topic_prefix}7detected/{class_name}"
        payload["timestamp"] = time.strftime("%Y-%m-%d %H:%M")
        self.client.publish(topic, json.dumps(payload))
        logger.debug(f"Published {topic}: {payload}")

    def publish_status(self, fps: float, running: bool):
        topic = f"{self.topic_prefix}status"
        payload = {"fps": fps, "running": running, "timestamp": time.strftime("%Y-%m-%d %H:%M")}
        self.client.publish(topic, json.dumps(payload))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

