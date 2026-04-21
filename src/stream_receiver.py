import cv2
import time
import logging

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
        self.using_fallback = False

    def connect(self) -> bool:
        logger.info("Connecting to RTSP stream...")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if self.cap.isOpened():
            logger.info("RTSP stream connected.")
            self.using_fallback = False
            return True
        logger.warning("RTSP connection failed.")
        return False

    def _connect_fallback(self) -> bool:
        logger.warning("Trying fallback: internal camera (index 0)...")
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            logger.info("Fallback camera connected.")
            self.using_fallback = True
            return True
        logger.error("Fallback camera also failed.")
        return False

    def connect_with_retry(self):
        attempts = 0
        while attempts < self.max_attempts:
            if self.connect():
                return
            attempts += 1
            logger.warning(f"Try {attempts}/{self.max_attempts} - waiting {self.reconnect_delay}s...")
            time.sleep(self.reconnect_delay)

        logger.warning("RTSP stream not reachable... switching to fallback camera.")
        if self._connect_fallback():
            return

        raise ConnectionError("RTSP stream and fallback camera both unavailable.")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            logger.warning("Stream lost... attempting reconnect!")
            try:
                self.connect_with_retry()
            except ConnectionError:
                return False, None

        ret, frame = self.cap.read()

        if not ret:
            logger.warning("Frame read failed... attempting reconnect!")
            self.release()
            try:
                self.connect_with_retry()
                reconnect_ret, reconnect_frame = self.cap.read()
                return reconnect_ret, reconnect_frame
            except ConnectionError:
                return False, None

        if self.using_fallback:
            cv2.putText(frame, "FALLBACK: Internal Camera", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return ret, frame

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Stream released.")

    def __enter__(self):
        self.connect_with_retry()
        return self

    def __exit__(self, *args):
        self.release()