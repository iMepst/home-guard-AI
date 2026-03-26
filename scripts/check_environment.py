import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check(label, fn):
    try:
        result = fn()
        print(f" {label}: {result}")
        return True
    except Exception as e:
        print(f" ERROR! {label}: {e}")
        return False


def main():
    print(f" Checking environment...")
    results = []

    print("[ Python ]")
    results.append(check("Version", lambda: sys.version.split()[0]))

    print("\n[ Libraries ]")
    results.append(check("OpenCV", lambda: __import__("cv2").__version__))
    results.append(check("Ultralytics", lambda: __import__("ultralytics").__version__))
    results.append(check("PyTorch", lambda: __import__("torch").__version__))
    results.append(check("paho-mqtt", lambda: __import__("paho.mqtt.client", fromlist=["client"]) and "ok"))
    results.append(check("pyyaml", lambda: __import__("yaml").__version__))
    results.append(check("dotenv", lambda: __import__("dotenv").__version__))

    print("\n[ Hardware ]")
    import torch
    results.append(check("MPS (Apple Neural Engine)",
                         lambda: "available" if torch.backends.mps.is_available() else (_ for _ in ()).throw(
                             Exception("not available"))))

    print("\n[ Netzwerk ]")
    import subprocess
    camera_ip = os.getenv("CAMERA_IP", "")
    mqtt_ip = os.getenv("MQTT_BROKER_IP", "")
    results.append(check(f"Ping Kamera ({camera_ip})",
                         lambda: "erreichbar" if subprocess.run(["ping", "-c", "1", "-W", "1000", camera_ip], capture_output=True).returncode == 0 else (_ for _ in ()).throw(
                             Exception("nicht erreichbar"))))
    results.append(check(f"Ping MQTT Broker ({mqtt_ip})",
                         lambda: "erreichbar" if subprocess.run(["ping", "-c", "1", "-W", "1000", mqtt_ip], capture_output=True).returncode == 0 else (_ for _ in ()).throw(
                             Exception("nicht erreichbar"))))

    print(f"\n{'='*40}")
    passed = sum(results)
    total  = len(results)
    print(f"  {passed}/{total} Checks bestanden")
    if passed == total:
        print("  Alles bereit. Pipeline kann starten!\n")
    else:
        print("  Bitte fehlgeschlagene Checks beheben.\n")

if __name__ == "__main__":
    main()