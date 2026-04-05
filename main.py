import cv2, logging
from src.config_loader import load_config
from src.stream_receiver import StreamReceiver
from src.detector import Detector
from src.mqtt_publisher import MQTTPublisher
from src.gesture_classifier import GestureClassifier
from src.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    config = load_config()
    cam_cfg   = config["camera"]
    mqtt_cfg  = config["mqtt"]
    model_cfg = config["model"]
    stream_cfg = config["stream"]
    gesture_cfg = config["gesture"]

    detector = Detector(
        model_path=model_cfg["path"],
        confidence=model_cfg["confidence_threshold"],
        classes=model_cfg["classes"],
        device=model_cfg["device"]
    )
    with StreamReceiver(
        rtsp_url=cam_cfg["rtsp_url"],
        reconnect_delay=stream_cfg["reconnect_delay"],
        max_attempts=stream_cfg["max_reconnect_attempts"]
    ) as stream, MQTTPublisher(
        broker=mqtt_cfg["broker"],
        port=mqtt_cfg["port"],
        topic_prefix=mqtt_cfg["topic_prefix"],
        username=mqtt_cfg["username"],
        password=mqtt_cfg["password"]
    ) as publisher, GestureClassifier(
        model_path=gesture_cfg["model_path"],
        min_confidence=gesture_cfg["min_confidence"]
    ) as gesture_classifier:

        Pipeline(stream, detector, gesture_classifier, publisher).run()

if __name__ == "__main__":
    main()