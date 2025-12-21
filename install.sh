#!/usr/bin/env bash

# YOLO installer and configuration script

set -e

CLR_BLUE='\033[94m'
CLR_GREEN='\033[92m'
CLR_YELLOW='\033[93m'
CLR_RED='\033[91m'
CLR_RESET='\033[0m'

echo -e "${CLR_BLUE}"
echo "==============================="
echo "        YOLO Installer"
echo "==============================="
echo -e "${CLR_RESET}"

# Resolve project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Detect Termux
if [[ -n "$TERMUX_VERSION" ]]; then
    ENV="termux"
    echo -e "${CLR_GREEN}Detected environment: Termux${CLR_RESET}"
else
    ENV="linux"
    echo -e "${CLR_GREEN}Detected environment: Linux${CLR_RESET}"
fi

echo

# Helper Functions
# ----------------

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_msg() {
    echo -e "${CLR_BLUE}• $1...${CLR_RESET}"
}

skip_msg() {
    echo -e "${CLR_GREEN}✓ $1 already installed${CLR_RESET}"
}

# Update package index
# --------------------
install_msg "Updating package index"

if [[ "$ENV" == "termux" ]]; then
    pkg update -y
else
    sudo apt update -y
fi

# Install system dependencies
# ---------------------------

# Python
if command_exists python3; then
    skip_msg "Python"
else
    install_msg "Installing Python"
    if [[ "$ENV" == "termux" ]]; then
        pkg install -y python
        pkg install -y python-pip
    else
        sudo apt install -y python3 python3-pip
    fi
fi

# Pip
if command_exists pip || command_exists pip3; then
    skip_msg "pip"
else
    install_msg "Installing pip"
    if [[ "$ENV" == "termux" ]]; then
        pkg install -y python-pip
    else
        python3 -m ensurepip --upgrade
    fi
fi

# FFmpeg
if command_exists ffmpeg; then
    skip_msg "FFmpeg"
else
    install_msg "Installing FFmpeg"
    if [[ "$ENV" == "termux" ]]; then
        pkg install -y ffmpeg
    else
        sudo apt install -y ffmpeg
    fi
fi

# Git (required for updates)
# --------------------------
if command_exists git; then
    skip_msg "git"
else
    install_msg "Installing git"
    if [[ "$ENV" == "termux" ]]; then
        pkg install -y git
    else
        sudo apt install -y git
    fi
fi

echo

# Install Python dependencies
# ---------------------------
install_msg "Installing Python dependencies"

cd "$PROJECT_ROOT"

if [[ "$ENV" == "termux" ]]; then
    # Termux: do not upgrade pip
    python3 -m pip install -r requirements.txt
else
    # Linux
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
fi

echo

# yt-dlp verification
# -------------------
if command_exists yt-dlp; then
    skip_msg "yt-dlp"
    echo -e "  Version: $(yt-dlp --version)"
else
    install_msg "Installing yt-dlp (stable)"
    python3 -m pip install -U yt-dlp
    echo -e "  Installed version: $(yt-dlp --version)"
fi

echo

# Deno
# ----
if command_exists deno; then
    skip_msg "Deno"
else
    install_msg "Installing Deno"
    if [[ "$ENV" == "termux" ]]; then
        pkg install -y deno || echo -e "${CLR_YELLOW}Deno install skipped${CLR_RESET}"
    else
        curl -fsSL https://deno.land/install.sh | sh || \
        echo -e "${CLR_YELLOW}Deno install skipped${CLR_RESET}"
    fi
fi

echo

# Compilation (python files)
# --------------------------
echo -e "${CLR_BLUE}Compiling python files...${CLR_RESET}"
python3 -m compileall -f -q yolo/

echo

# Permissions
# -----------
install_msg "Setting executable permissions"

chmod +x install.sh
chmod +x run.sh
chmod +x yolo/updater/*.sh

echo

# Alias setup
# -----------
SHELL_RC="$HOME/.bashrc"

if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if grep -q "alias yolo=" "$SHELL_RC" 2>/dev/null; then
    echo -e "${CLR_GREEN}Alias 'yolo' already added${CLR_RESET}"
else
    install_msg "Adding 'yolo' alias"
    echo "alias yolo='$PROJECT_ROOT/run.sh'" >> "$SHELL_RC"
    echo -e "${CLR_GREEN}Alias added to $SHELL_RC${CLR_RESET}"
    source "$SHELL_RC" 2>/dev/null || true
    echo -e "${CLR_YELLOW}If 'yolo' command doesn't work, restart your terminal.${CLR_RESET}"
fi

echo

# Final verification
# ------------------
echo -e "${CLR_GREEN}Installation Complete${CLR_RESET}"
echo
echo "Versions:"
echo "  Python : $(python3 --version)"
echo "  yt-dlp : $(yt-dlp --version)"
echo "  FFmpeg : $(ffmpeg -version | head -n 1)"
echo
echo -e "${CLR_GREEN}Run 'yolo' to start the program.${CLR_RESET}"
