import cv2
import time
import logging
from src.config_loader import load_config

# logger init for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger(__name__)

# connecting to stream and error handling
class StreamReceiver:
    def __init__(self, rtsp_url: str, reconnect_delay: int = 5, max_attempts: int = 5):
        self.rtsp_url = rtsp_url
        self.reconnect_delay = reconnect_delay
        self.max_attempts = max_attempts
        self.cap = None

    def connect(self) -> bool:
        logger.info("Connecting to Stream...")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if self.cap.isOpened():
            logger.info("Stream connected.")
            return True
        logger.warning("Connection with Stream failed.")
        return False

    def connect_with_retry(self):
        attempts = 0
        while attempts < self.max_attempts:
            if self.connect():
                return
            attempts += 1
            logger.warning(f"Try {attempts}/{self.max_attempts} - waiting {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)
        raise ConnectionError(f"Stream is not established after {self.max_attempts} tries")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Stream released.")

    def __enter__(self):
        self.connect_with_retry()
        return self

    def __exit__(self, *args):
        self.release()

if __name__ == "__main__":
    config = load_config()

    fps_counter = 0
    fps_display = 0
    fps_timer = 0

    with StreamReceiver(
        rtsp_url=config["camera"]["rtsp_url"],
        reconnect_delay=config["stream"]["reconnect_delay"],
        max_attempts=config["stream"]["max_reconnect_attempts"]
    ) as stream:
        logger.info("Stream is running... Press ESC to exit.")
        while True:
            ret, frame = stream.read_frame()
            if not ret:
                logger.warning("Frame could not be read.")
                break

            # fps counter displayed in stream frame
            fps_counter += 1
            if time.time() - fps_timer >= 1.0:
                fps_display = fps_counter
                fps_counter = 0
                fps_timer = time.time()

            cv2.putText(frame, f"FPS: {fps_display}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("HomeGuard AI Stream", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    cv2.destroyAllWindows()


