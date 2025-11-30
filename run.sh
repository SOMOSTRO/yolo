#!/usr/bin/env bash

# YOLO launcher script

# Resolve script's real location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to project root
cd "$SCRIPT_DIR" || {
  echo "Failed to change directory to YOLO project root."
  exit 1
}

# Detect python executable
if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "Error: Python is not installed."
  echo "Please install python and try again."
  exit 1
fi

# Clear terminal screen
# clear

# Run YOLO as a module
exec "$PY" -m yolo.main "$@"