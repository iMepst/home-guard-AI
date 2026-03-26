import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# replaces ${VAR} placeholders with env vars
def _resolve_env_vars (value: str) -> str:
    import re
    def replacer(match):
        var_name = match.group(1)
        result = os.getenv(var_name, "")
        if not result:
            raise ValueError(f"Umgebungsvariable '{var_name}' ist nicht gesetzt.")
        return result
    return re.sub(r'\$\{(\w+)}', replacer, value)

# recursive config dictionary, resolves all env vars
def _resolve_dict (d: dict) -> dict:
    resolved = {}
    for key, value in d.items():
        if isinstance(value, dict):
            resolved[key] = _resolve_dict (value)
        elif isinstance(value, str):
            resolved[key] = _resolve_env_vars (value)
        else:
            resolved[key] = value
    return resolved

def load_config (path: str = "config/config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r") as f:
        raw = yaml.safe_load (f)

    return _resolve_dict (raw)

if __name__ == "__main__":
    config = load_config()
    print("RTSP URL:   ", config["camera"]["rtsp_url"])
    print("MQTT Broker:", config["mqtt"]["broker"])
    print("Modell:     ", config["model"]["path"])
    print("Device:     ", config["model"]["device"])