#!/usr/bin/env bash

# YODO launcher script

# Resolve script's real location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -t 1 ]; then
    CLR_RED=$'\033[91m'
    CLR_RESET=$'\033[0m'
else
    CLR_RED=''
    CLR_RESET=''
fi

# Change to project root
cd "$SCRIPT_DIR" || {
  echo -e "${CLR_RED}Failed to change directory to YODO project root.${CLR_RESET}"
  exit 1
}

# Detect python executable
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo -e "${CLR_RED}Error: Python is not installed.${CLR_RESET}"
  echo -e "${CLR_RED}Please install python and try again.${CLR_RESET}"
  exit 1
fi

# Clear terminal screen if the no of args is 0
if [ "$#" -eq 0 ]; then
  clear
fi

# Run YODO as a module
exec "$PY" -m yodo.main "$@"
