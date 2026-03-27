import torch
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class Detector:
    def __init__(self, model_path: str, classes: str, confidence: float, device: str):
        self.confidence = confidence
        self.classes = classes
        self.device = device
        logger.info(f"Loading model... {model_path} on {device}")
        self.model = YOLO(model_path)
        self.model.to(device)
        logger.info("Model loaded!")

    def detect(self, frame):
        results = self.model(frame, conf=self.confidence, device=self.device, classes=self.classes, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                detections.append({
                    "class_id": int(box.cls),
                    "class_name": self.model.names[int(box.cls)],
                    "confidence": round(float(box.conf), 2),
                    "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
                })
        return detections

if "__main__" == __name__:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    import cv2
    import time
    from config_loader import load_config
    from stream_receiver import StreamReceiver

    config = load_config()
    detector = Detector(
        model_path=config["model"]["path"],
        classes=config["model"]["classes"],
        confidence=config["model"]["confidence_threshold"],
        device=config["model"]["device"]
    )

    fps_counter = 0
    fps_display = 0
    fps_timer = time.time()

    with StreamReceiver(
            rtsp_url=config["camera"]["rtsp_url"],
            reconnect_delay=config["stream"]["reconnect_delay"],
            max_attempts=config["stream"]["max_reconnect_attempts"]
    ) as stream:
        logger.info("Detector ist running... press ESC to stop")
        while True:
            ret, frame = stream.read_frame()
            if not ret:
                break

            detections = detector.detect(frame)

            for d in detections:
                x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
                label = f"{d['class_name']} {d['confidence']}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            fps_counter += 1
            if time.time() - fps_timer >= 1.0:
                fps_display = fps_counter
                fps_counter = 0
                fps_timer = time.time()

            cv2.putText(frame, f"FPS: {fps_display}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("HomeGuard AI Detector", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    cv2.destroyAllWindows()