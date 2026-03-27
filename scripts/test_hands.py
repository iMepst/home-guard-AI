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

# HandLandmarker config
base_options = mp_python.BaseOptions(model_asset_path="models/hand_landmarker.task")
options = mp_vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=mp_vision.RunningMode.VIDEO
)

with mp_vision.HandLandmarker.create_from_options(options) as landmarker, \
     StreamReceiver(
         rtsp_url=config["camera"]["rtsp_url"],
         reconnect_delay=config["stream"]["reconnect_delay"],
         max_attempts=config["stream"]["max_reconnect_attempts"]
     ) as stream:

    print("Stream läuft – zeig deine Hand. ESC zum Beenden.")
    timestamp_ms = 0

    while True:
        ret, frame = stream.read_frame()
        if not ret:
            break

        timestamp_ms += 33  # ~30fps simulation

        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = landmarker.detect_for_video(mp_img, timestamp_ms)

        if results.hand_landmarks:
            for hand in results.hand_landmarks:
                # Keypoints auf Frame zeichnen
                h, w, _ = frame.shape
                for lm in hand:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

                # Wrist Keypoint ausgeben
                wrist = hand[0]
                print(f"Wrist: x={wrist.x:.2f} y={wrist.y:.2f}", end="\r")

        cv2.imshow("MediaPipe Hands Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cv2.destroyAllWindows()