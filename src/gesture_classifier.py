import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import logging, time

logger = logging.getLogger(__name__)

# MediaPipe names mapping to HA actions
GESTURE_MAP = {
    "Open_Palm":   "open_hand",
    "Closed_Fist": "fist",
    "Thumb_Up":    "thumb_up",
    "Thumb_Down":  "thumb_down"
}

class GestureClassifier:
    def __init__(self, model_path: str, min_confidence: float = 0.7):
        self.start_time = time.time()
        self.min_confidence = min_confidence
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.GestureRecognizerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=min_confidence,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=mp_vision.RunningMode.VIDEO
        )
        self.recognizer= mp_vision.GestureRecognizer.create_from_options(options)
        self.timestamp_ms = 0
        logger.info(f"Gesture Classifier initialized successfully")

    def recognize(self, frame):
        self.timestamp_ms = int((time.time() - self.start_time) * 1000)

        rgb    = __import__("cv2").cvtColor(frame, __import__("cv2").COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.recognizer.recognize_for_video(mp_img, self.timestamp_ms)
        print(f"gestures={len(results.gestures)} hands={len(results.hand_landmarks)}", end="\r")

        if not results.gestures:
            return None

        gesture    = results.gestures[0][0]
        confidence = round(gesture.score, 2)
        name       = GESTURE_MAP.get(gesture.category_name)

        if name is None or confidence < self.min_confidence:
            return None

        return {"gesture": name, "confidence": confidence}

    def close(self):
        self.recognizer.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()