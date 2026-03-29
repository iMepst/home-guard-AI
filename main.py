import cv2
import time
import logging
from src.config_loader import load_config
from src.stream_receiver import StreamReceiver
from src.detector import Detector
from src.mqtt_publisher import MQTTPublisher
from src.gesture_classifier import GestureClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    config = load_config()
    cam_cfg   = config["camera"]
    mqtt_cfg  = config["mqtt"]
    model_cfg = config["model"]
    stream_cfg = config["stream"]

    detector = Detector(
        model_path=model_cfg["path"],
        confidence=model_cfg["confidence_threshold"],
        classes=model_cfg["classes"],
        device=model_cfg["device"]
    )

    gesture_classifier = GestureClassifier(
        model_path="models/gesture_recognizer.task",
        min_confidence=0.7
    )

    fps_counter = 0
    fps_display = 0
    fps_timer   = time.time()
    status_timer = time.time()

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
    ) as publisher:

        logger.info("Pipeline läuft – ESC zum Beenden")

        while True:
            ret, frame = stream.read_frame()
            if not ret:
                logger.warning("Frame konnte nicht gelesen werden.")
                break

            detections = detector.detect(frame)

            for d in detections:
                # publish MQTT
                publisher.publish(d["class_name"], {
                    "confidence": d["confidence"],
                    "bbox":       d["bbox"]
                })

                # create Bounding Box
                x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
                label = f"{d['class_name']} {d['confidence']}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            gesture = gesture_classifier.recognize(frame)
            print(f"DEBUG gesture: {gesture}", end="\r")
            if gesture:
                publisher.publish("gesture", gesture)
                cv2.putText(frame, f"Geste: {gesture['gesture']} ({gesture['confidence']})",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # calculate FPS
            fps_counter += 1
            if time.time() - fps_timer >= 1.0:
                fps_display = fps_counter
                fps_counter = 0
                fps_timer   = time.time()

            # publish status every 10s
            if time.time() - status_timer >= 10.0:
                publisher.publish_status(fps=fps_display, running=True)
                status_timer = time.time()

            cv2.putText(frame, f"FPS: {fps_display}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("HomeGuard AI", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    cv2.destroyAllWindows()
    publisher.publish_status(fps=0, running=False)
    logger.info("Pipeline beendet.")

if __name__ == "__main__":
    main()