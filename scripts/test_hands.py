import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config_loader import load_config
from src.stream_receiver import StreamReceiver

config = load_config()

base_options = mp_python.BaseOptions(model_asset_path="models/gesture_recognizer.task")
options = mp_vision.GestureRecognizerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=mp_vision.RunningMode.VIDEO
)

with mp_vision.GestureRecognizer.create_from_options(options) as recognizer, \
     StreamReceiver(
         rtsp_url=config["camera"]["rtsp_url"],
         reconnect_delay=config["stream"]["reconnect_delay"],
         max_attempts=config["stream"]["max_reconnect_attempts"]
     ) as stream:

    print("Stream is running... press ESC to quit.")
    timestamp_ms = 0

    while True:
        ret, frame = stream.read_frame()
        if not ret:
            break

        timestamp_ms += 33

        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = recognizer.recognize_for_video(mp_img, timestamp_ms)

        if results.gestures:
            gesture    = results.gestures[0][0]
            name       = gesture.category_name
            confidence = round(gesture.score, 2)
            print(f"Gesture: {name:<20} Confidence: {confidence}", end="\r")
            cv2.putText(frame, f"{name} ({confidence})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if results.hand_landmarks:
            h, w, _ = frame.shape
            for lm in results.hand_landmarks[0]:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        cv2.imshow("Gesture Recognizer Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cv2.destroyAllWindows()