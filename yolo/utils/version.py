import json
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parents[2] / "version.json"

def _version_json_data():
  """Read and return version file data"""
  try:
    with open(VERSION_FILE, "r") as f:
      return json.load(f)
  except Exception:
    return {}

def get_version():
  """Return YOLO version from version.json"""
  return _version_json_data.get("version", "unknown")


def get_channel():
  """Return release channel from version.json"""
  return _version_json_data.get("channel", "unknown")