import cv2
import time
import logging

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, stream, detector, gesture_classifier, publisher):
        self.stream             = stream
        self.detector           = detector
        self.gesture_classifier = gesture_classifier
        self.publisher          = publisher

    def _process_detections(self, frame, detections):
        for d in detections:
            self.publisher.publish(d["class_name"], {
                "confidence": d["confidence"],
                "bbox":       d["bbox"]
            })
            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
            label = f"{d['class_name']} {d['confidence']}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    def _process_gesture(self, frame):
        gesture = self.gesture_classifier.recognize(frame)
        if gesture:
            self.publisher.publish("gesture", gesture, dedup_key=gesture["gesture"])
            cv2.putText(frame, f"Geste: {gesture['gesture']} ({gesture['confidence']})",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    def run(self):
        fps_counter  = 0
        fps_display  = 0
        fps_timer    = time.time()
        status_timer = time.time()

        logger.info("Pipeline is running... press ESC to quit")

        while True:
            ret, frame = self.stream.read_frame()
            if not ret:
                logger.error("Stream nicht wiederherstellbar – Pipeline wird beendet.")
                break

            self._process_detections(frame, self.detector.detect(frame))
            self._process_gesture(frame)

            # FPS
            fps_counter += 1
            if time.time() - fps_timer >= 1.0:
                fps_display = fps_counter
                fps_counter = 0
                fps_timer   = time.time()

            # Status alle 10s
            if time.time() - status_timer >= 10.0:
                self.publisher.publish_status(fps=fps_display, running=True)
                status_timer = time.time()

            cv2.putText(frame, f"FPS: {fps_display}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("HomeGuard AI", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cv2.destroyAllWindows()
        self.publisher.publish_status(fps=0, running=False)
        logger.info("Pipeline terminated.")