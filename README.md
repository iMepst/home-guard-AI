# HomeGuard AI

> A local, real-time computer vision pipeline that understands scenes and controls smart home devices — no cloud required.

---

## Overview

HomeGuard AI connects an IP camera to a local AI pipeline built on YOLOv8 and MediaPipe. The system detects objects, recognizes hand gestures, and publishes structured events via MQTT to Home Assistant — enabling gesture-controlled smart home automation.

**Current capabilities:**
- Real-time object detection via YOLOv8 (MPS-accelerated on Apple Silicon)
- Hand gesture recognition via MediaPipe Gesture Recognizer
- Structured MQTT event publishing with throttling & deduplication
- Home Assistant automation triggers via gesture input
- Fully local — no cloud dependency

---

## Hardware

| Component | Role |
|---|---|
| Reolink P850 PoE | Video source (RTSP stream) |
| MacBook M1 Pro | AI pipeline (Phase 1 & 2) |
| Raspberry Pi 5 8 GB | Home Assistant OS / MQTT Broker |
| Jetson Nano *(planned)* | Edge AI worker (Phase 3+) |
| PoE Switch / Injector | Camera power supply |

> All devices must be on the same local network.

---

## Architecture

```
Reolink P850 (RTSP)
        │
        ▼
MacBook M1 Pro
  ├── StreamReceiver     (OpenCV RTSP + reconnect logic)
  ├── Detector           (YOLOv8n, MPS-accelerated)
  ├── GestureClassifier  (MediaPipe Gesture Recognizer)
  ├── Pipeline           (frame loop orchestration)
  └── MQTTPublisher      (throttled, deduplicated events)
        │
        ▼
Raspberry Pi 5 (Home Assistant OS)
  ├── Mosquitto Broker
  └── HA Automations
        │
        ▼
Smart Devices (lights, audio, etc.)
```

In Phase 3, the **Jetson Nano** replaces the MacBook as the AI worker.

---

## Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 – Foundation | Done | RTSP stream → YOLOv8 → MQTT → Home Assistant |
| 2 – Gestures | Done | MediaPipe hand gesture recognition → HA automations |
| 3 – Edge Deployment | 🔜 Planned | Migration to Jetson Nano, ONNX / TensorRT optimization |
| 4 – Monitoring | 🔜 Planned | InfluxDB + Grafana activity logging & dashboards |

---

## Project Structure

```
homeGuardAI/
│
├── config/
│   └── config.yaml              # Central configuration
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py         # YAML + .env variable resolution
│   ├── stream_receiver.py       # RTSP connection & reconnect logic
│   ├── detector.py              # YOLOv8 inference
│   ├── gesture_classifier.py    # MediaPipe gesture recognition
│   ├── mqtt_publisher.py        # MQTT client with throttling & dedup
│   └── pipeline.py              # Frame loop orchestration
│
├── models/                      # Model files (gitignored)
│
├── data/
│   ├── raw/                     # Raw training images
│   ├── labeled/                 # Labeled datasets
│   └── exports/                 # ONNX / TensorRT exports
│
├── tests/
│   ├── test_stream.py
│   ├── test_detector.py
│   └── test_mqtt.py
│
├── scripts/
│   ├── check_environment.py     # Setup verification
│   ├── test_hands.py            # MediaPipe hands debug script
│   └── benchmark_fps.py         # FPS benchmark tool
│
├── notebooks/
│   └── explore_detections.ipynb
│
├── conftest.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.11 (via pyenv recommended)
- Mosquitto Add-on active in Home Assistant OS
- RTSP stream URL of your camera

### Installation

```bash
git clone https://github.com/your-user/homeGuardAI.git
cd homeGuardAI

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Fill in your credentials in `.env`:

```
CAMERA_USER=your_user
CAMERA_PASSWORD=your_password
CAMERA_IP=192.168.x.x
MQTT_BROKER_IP=192.168.x.x
MQTT_USER=your_mqtt_user
MQTT_PASSWORD=your_mqtt_password
```

Edit `config/config.yaml` for model and pipeline settings:

```yaml
model:
  path: "models/yolov8n.pt"
  confidence_threshold: 0.5
  device: "mps"        # mps (Apple Silicon), cuda (Jetson), cpu

gesture:
  model_path: "models/gesture_recognizer.task"
  min_confidence: 0.7
  throttle_seconds: 2
```

### Verify Setup

```bash
python scripts/check_environment.py
```

### Run

```bash
python main.py
```

---

## Supported Gestures

| Gesture | Action |
|---|---|
| Open Palm | Light on |
| Closed Fist | Light off |
| Thumb Up | Music play |
| Thumb Down | Music pause |

---

## MQTT Topics

| Topic | Description | Payload |
|---|---|---|
| `homeai/detected/{class}` | Object detected | `{"confidence": 0.92, "bbox": [...], "timestamp": "..."}` |
| `homeai/detected/gesture` | Gesture detected | `{"gesture": "thumb_up", "confidence": 0.88, "timestamp": "..."}` |
| `homeai/status` | Pipeline heartbeat | `{"fps": 14.2, "running": true, "timestamp": "..."}` |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Dependencies

```
ultralytics>=8.0
opencv-python>=4.8
paho-mqtt>=2.0
pyyaml>=6.0
numpy>=1.24
mediapipe>=0.10
python-dotenv>=1.0
pytest>=7.0
```

---

## License

MIT License — see `LICENSE`
