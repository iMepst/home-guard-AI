import pytest
from unittest.mock import MagicMock, patch
from src.stream_receiver import StreamReceiver

@pytest.fixture
def stream():
    with patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.isOpened.return_value = True
        s = StreamReceiver(rtsp_url="rtsp://fake/stream")
        s.cap = mock_cap.return_value
        yield s

def test_connect_success(stream):
    """Stream verbindet sich erfolgreich."""
    assert stream.connect() == True

def test_read_frame_success(stream):
    """Frame wird erfolgreich gelesen."""
    stream.cap.read.return_value = (True, MagicMock())
    ret, frame = stream.read_frame()
    assert ret == True
    assert frame is not None

def test_read_frame_reconnect(stream):
    """Bei fehlgeschlagenem Frame wird Reconnect versucht."""
    stream.cap.read.return_value = (False, None)
    stream.cap.isOpened.return_value = False
    with patch.object(stream, "connect_with_retry") as mock_reconnect:
        mock_reconnect.side_effect = ConnectionError("Stream nicht erreichbar")
        ret, frame = stream.read_frame()
        assert ret == False
        assert frame is None

def test_release(stream):
    """Stream wird sauber freigegeben."""
    stream.release()
    stream.cap.release.assert_called_once()