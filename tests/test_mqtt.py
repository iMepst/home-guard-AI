import pytest
import time
from unittest.mock import MagicMock, patch
from src.mqtt_publisher import MQTTPublisher

@pytest.fixture
def publisher():
    with patch("paho.mqtt.client.Client") as mock_client:
        pub = MQTTPublisher(
            broker="localhost",
            port=1883,
            topic_prefix="homeai",
            username="",
            password=""
        )
        pub.connected = True
        pub.client = MagicMock()
        yield pub

def test_publish_throttle(publisher):
    """Gleiche Klasse darf nicht zu schnell zweimal publiziert werden."""
    publisher.publish("person", {"confidence": 0.9, "bbox": [0, 0, 100, 100]})
    publisher.publish("person", {"confidence": 0.9, "bbox": [0, 0, 100, 100]})
    assert publisher.client.publish.call_count == 1

def test_publish_different_classes(publisher):
    """Verschiedene Klassen werden unabhängig voneinander throttled."""
    publisher.publish("person", {"confidence": 0.9, "bbox": [0, 0, 100, 100]})
    publisher.publish("car",    {"confidence": 0.8, "bbox": [0, 0, 200, 200]})
    assert publisher.client.publish.call_count == 2

def test_publish_gesture_dedup(publisher):
    """Gleiche Geste wird nicht zweimal hintereinander publiziert."""
    publisher.publish("gesture", {"gesture": "thumb_up", "confidence": 0.9}, dedup_key="thumb_up")
    publisher.publish("gesture", {"gesture": "thumb_up", "confidence": 0.9}, dedup_key="thumb_up")
    assert publisher.client.publish.call_count == 1

def test_publish_not_connected(publisher):
    """No publish if not connected"""
    publisher.connected = False
    publisher.publish("person", {"confidence": 0.9, "bbox": [0, 0, 100, 100]})
    assert publisher.client.publish.call_count == 0