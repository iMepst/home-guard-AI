# HomeGuard AI

> Intelligentes Raumverständnis-System auf Basis von YOLOv8, RTSP-Streaming und Home Assistant – vollständig lokal, ohne Cloud.

---

## Projektübersicht

HomeGuard AI verbindet eine IP-Kamera mit einer lokalen KI-Pipeline. Das System erkennt nicht nur *was* im Bild ist, sondern versteht den *Kontext* einer Szene und löst darauf basierend smarte Home-Assistant-Automatisierungen aus.

**Kernfunktionen (geplant):**
- Echtzeit-Personen- und Objekterkennung via YOLOv8
- Gestensteuerung für Smart-Home-Geräte
- Aktivitätserkennung (sitzen, gehen, schlafen)
- Anomalie-Erkennung mit MQTT-Alerts
- Vollständig lokal – keine Cloud-Abhängigkeit

---

## Hardware

| Komponente | Rolle |
|---|---|
| Reolink P850 PoE | Videoquelle (RTSP-Stream) |
| MacBook M1 Pro 32 GB | AI-Pipeline (Phase 1 & 2) |
| Raspberry Pi 5 8 GB | Home Assistant OS / MQTT Broker |
| Jetson Nano *(geplant)* | Edge AI Worker (Phase 3+) |
| PoE-Switch / Injector | Stromversorgung der Kamera |

> Alle Geräte müssen sich im selben lokalen Netzwerk befinden.

---

## Systemarchitektur

```
Reolink P850 (RTSP)
        │
        ▼
MacBook M1 Pro
  ├── OpenCV Stream Receiver
  ├── YOLOv8 Inferenz (MPS)
  ├── Gesture Classifier
  ├── Scene Interpreter
  └── MQTT Publisher
        │
        ▼
Raspberry Pi 5 (HAOS)
  ├── Mosquitto Broker
  ├── Home Assistant Automations
  └── Node-RED Flows
        │
        ▼
Smarte Geräte (Licht, Audio, etc.)
```

In Phase 3 ersetzt der **Jetson Nano** das MacBook als AI-Worker.

---

## Projektphasen

### Phase 1 – Fundament *(aktuell)*
Stabiler RTSP-Stream → YOLOv8-Inferenz → MQTT-Events an Home Assistant.

### Phase 2 – Gesten & Kontext
Eigenes Gesten-Dataset aufnehmen, trainieren und als zweite Erkennungsstufe integrieren. Scene Interpreter für zeitbasierte Aktivitätserkennung.

### Phase 3 – Edge Deployment
Migration der AI-Pipeline auf den Jetson Nano. Modell-Optimierung via ONNX / TensorRT. Ziel: <200 ms Latenz.

### Phase 4 – Monitoring & Logging
InfluxDB + Grafana für Aktivitäts-Logs und Performance-Dashboards.

---

## Projektstruktur

```
homeGuardAI/
│
├── config/
│   └── config.yaml              # Zentrale Konfiguration (RTSP, MQTT, Modell)
│
├── src/
│   ├── __init__.py
│   ├── stream_receiver.py       # RTSP-Verbindung & Frame-Loop
│   ├── detector.py              # YOLOv8 Inferenz & MPS-Setup
│   ├── scene_interpreter.py     # Kontext-Logik (Phase 2+)
│   ├── gesture_classifier.py    # Gesten-Erkennung (Phase 2+)
│   └── mqtt_publisher.py        # MQTT-Client & Payload-Builder
│
├── models/
│   └── yolov8n.pt               # Modell-Dateien (gitignored)
│
├── data/
│   ├── raw/                     # Rohe Trainingsbilder
│   ├── labeled/                 # Gelabelte Daten
│   └── exports/                 # ONNX / TensorRT Exports
│
├── tests/
│   ├── test_stream.py
│   ├── test_detector.py
│   └── test_mqtt.py
│
├── scripts/
│   ├── check_environment.py     # Setup-Verifikation
│   └── benchmark_fps.py         # FPS-Benchmark Tool
│
├── notebooks/
│   └── explore_detections.ipynb
│
├── main.py                      # Pipeline-Einstiegspunkt
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### Voraussetzungen

- Python 3.11
- Mosquitto Add-on in Home Assistant OS aktiv
- RTSP-Stream der Reolink bekannt und erreichbar

### Installation

```bash
# Repository klonen
git clone https://github.com/dein-user/homeGuardAI.git
cd homeGuardAI

# Virtuelle Umgebung erstellen
python3.11 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Konfiguration

```bash
# Konfigurationsdatei anpassen
cp config/config.yaml.example config/config.yaml
```

```yaml
# config/config.yaml
camera:
  rtsp_url: "rtsp://user:password@192.168.1.x/stream"

mqtt:
  broker: "192.168.1.x"   # IP des Raspberry Pi
  port: 1883
  topic_prefix: "homeai"

model:
  path: "models/yolov8n.pt"
  confidence_threshold: 0.5
  device: "mps"            # mps (M1), cuda (Jetson), cpu
```

### Umgebung prüfen

```bash
python scripts/check_environment.py
```

### Starten

```bash
python main.py
```

---

## MQTT Topics

| Topic | Beschreibung | Payload Beispiel |
|---|---|---|
| `homeai/detected/person` | Person erkannt | `{"confidence": 0.92, "bbox": [x,y,w,h], "timestamp": "..."}` |
| `homeai/detected/object` | Objekt erkannt | `{"class": "chair", "confidence": 0.85, ...}` |
| `homeai/gesture` | Geste erkannt | `{"gesture": "wave", "confidence": 0.78, ...}` |
| `homeai/activity` | Aktivitätsstatus | `{"activity": "working", "duration_sec": 300}` |
| `homeai/status` | Pipeline-Status | `{"fps": 18.3, "running": true}` |

---

## Abhängigkeiten

```
ultralytics>=8.0
opencv-python>=4.8
paho-mqtt>=2.0
pyyaml>=6.0
numpy>=1.24
```

---

## Lernziele dieses Projekts

- Edge AI auf ARM / CUDA-Hardware deployen
- Echtzeit-Pipelines mit OpenCV optimieren
- Multimodale Systeme (Video + MQTT) aufbauen
- Eigene Datasets aufnehmen, labeln und trainieren
- Home Assistant via MQTT programmatisch steuern

---

## Lizenz

MIT License – siehe `LICENSE`