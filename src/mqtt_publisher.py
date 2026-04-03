import json
import logging
import time
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("MQTT verbunden")
        userdata.connected = True
    else:
        logger.error(f"MQTT Verbindung fehlgeschlagen: {reason_code}")


def _on_disconnect(client, userdata, flags, reason_code, properties):
    logger.warning("MQTT getrennt.")
    userdata.connected = False


class MQTTPublisher:
    def __init__(self, broker: str, port: int, topic_prefix: str, username: str = "", password: str = ""):
        self.broker = broker
        self.port = port
        self.topic_prefix = topic_prefix
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.user_data_set(self)
        self._last_published: dict = {}
        self._last_payload: dict = {}
        self.connected = False
        self.throttle_seconds = 3  # Nur alle 3 Sekunden pro Klasse publizieren

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = _on_connect
        self.client.on_disconnect = _on_disconnect

    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def disconnect(self):
        try:
            self.publish_status(fps=0, running=False)
        except (RuntimeError, ValueError) as e:
            logger.debug(f"Failed to publish shutdown status: {e}")
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, class_name: str, payload: dict):
        if not self.connected:
            return

        now = time.time()
        last = self._last_published.get(class_name, 0)

        # throttle
        if now - last < self.throttle_seconds:
            return

        # deduplicate payload
        last_payload = self._last_payload.get(class_name)
        if last_payload == payload:
            return

        self._last_published[class_name] = now
        self._last_payload[class_name] = payload.copy()

        topic = f"{self.topic_prefix}/detected/{class_name}"
        payload["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")

        self.client.publish(topic, json.dumps(payload), qos=1)
        logger.debug(f"Published {topic}: {payload}")

    def publish_status(self, fps: float, running: bool):
        if not self.connected:
            return

        topic = f"{self.topic_prefix}/status"
        payload = {
            "fps": round(fps, 2),
            "running": running,
            "timestamp": time.strftime("%Y-%m-%d %H:%M")
        }

        self.client.publish(topic, json.dumps(payload), qos=1, retain=True)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

